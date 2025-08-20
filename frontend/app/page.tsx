'use client'

import { useState, useEffect } from 'react'
import SearchForm from '../components/SearchForm'
import SearchResults from '../components/SearchResults'
import LoadingSpinner from '../components/LoadingSpinner'

export interface SearchResult {
  source: string
  title: string
  url: string
  snippet: string
  timestamp?: string
  score?: number
}

export interface SearchResponse {
  query: string
  results: Record<string, SearchResult[]>
  ai_synthesis?: string
  search_duration: number
  total_results: number
}

export default function Home() {
  const [isSearching, setIsSearching] = useState(false)
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [streamingResults, setStreamingResults] = useState<Record<string, SearchResult[]>>({})
  const [isStreaming, setIsStreaming] = useState(false)

  const handleSearch = async (query: string, sources: string[], useStreaming: boolean = false) => {
    setError(null)
    setSearchResponse(null)
    setStreamingResults({})
    
    if (useStreaming) {
      handleStreamingSearch(query, sources)
    } else {
      handleRegularSearch(query, sources)
    }
  }

  const handleRegularSearch = async (query: string, sources: string[]) => {
    setIsSearching(true)
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          sources,
          max_results_per_source: 5
        }),
      })

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`)
      }

      const data: SearchResponse = await response.json()
      setSearchResponse(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setIsSearching(false)
    }
  }

  const handleStreamingSearch = async (query: string, sources: string[]) => {
    setIsStreaming(true)
    setStreamingResults({})
    
    try {
      const sourcesParam = sources.join(',')
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/search/stream/${encodeURIComponent(query)}?sources=${sourcesParam}`
      )

      if (!response.ok) {
        throw new Error(`Streaming search failed: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      const decoder = new TextDecoder()
      
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break
        
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.type === 'results') {
                setStreamingResults(prev => ({
                  ...prev,
                  [data.source]: data.results
                }))
              } else if (data.type === 'error') {
                console.error(`Error from ${data.source}:`, data.error)
              } else if (data.type === 'complete') {
                // Stream completed
                break
              }
            } catch (parseError) {
              console.error('Error parsing streaming data:', parseError)
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Streaming search failed')
    } finally {
      setIsStreaming(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <SearchForm onSearch={handleSearch} isSearching={isSearching || isStreaming} />
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-700">{error}</p>
        </div>
      )}
      
      {(isSearching || isStreaming) && (
        <div className="flex justify-center mb-6">
          <LoadingSpinner />
        </div>
      )}
      
      {searchResponse && (
        <SearchResults response={searchResponse} />
      )}
      
      {isStreaming && Object.keys(streamingResults).length > 0 && (
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-4">Live Results</h2>
          <SearchResults 
            response={{
              query: '',
              results: streamingResults,
              search_duration: 0,
              total_results: Object.values(streamingResults).flat().length
            }} 
          />
        </div>
      )}
    </div>
  )
}
