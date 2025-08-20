'use client'

import { useState } from 'react'
import { Search, Globe, Loader2 } from 'lucide-react'

interface SearchFormProps {
  onSearch: (query: string, sources: string[], useStreaming?: boolean) => void
  isSearching: boolean
}

const availableSources = [
  { id: 'google', name: 'Google', color: 'bg-blue-500' },
  { id: 'duckduckgo', name: 'DuckDuckGo', color: 'bg-orange-500' },
  { id: 'wikipedia', name: 'Wikipedia', color: 'bg-gray-600' },
]

export default function SearchForm({ onSearch, isSearching }: SearchFormProps) {
  const [query, setQuery] = useState('')
  const [selectedSources, setSelectedSources] = useState<string[]>(['google', 'duckduckgo', 'wikipedia'])
  const [useStreaming, setUseStreaming] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim() && selectedSources.length > 0) {
      onSearch(query.trim(), selectedSources, useStreaming)
    }
  }

  const toggleSource = (sourceId: string) => {
    setSelectedSources(prev => 
      prev.includes(sourceId) 
        ? prev.filter(id => id !== sourceId)
        : [...prev, sourceId]
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Search Input */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your search query..."
            className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-lg"
            disabled={isSearching}
          />
        </div>

        {/* Source Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Select Search Sources:
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {availableSources.map((source) => (
              <label
                key={source.id}
                className={`relative flex items-center p-3 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedSources.includes(source.id)
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                } ${isSearching ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <input
                  type="checkbox"
                  checked={selectedSources.includes(source.id)}
                  onChange={() => toggleSource(source.id)}
                  disabled={isSearching}
                  className="sr-only"
                />
                <div className={`w-4 h-4 rounded ${source.color} mr-3 flex items-center justify-center`}>
                  <Globe className="w-3 h-3 text-white" />
                </div>
                <span className="text-sm font-medium text-gray-700">{source.name}</span>
                {selectedSources.includes(source.id) && (
                  <div className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full"></div>
                )}
              </label>
            ))}
          </div>
        </div>

        {/* Streaming Option */}
        <div className="flex items-center">
          <input
            id="streaming"
            type="checkbox"
            checked={useStreaming}
            onChange={(e) => setUseStreaming(e.target.checked)}
            disabled={isSearching}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label htmlFor="streaming" className="ml-2 text-sm text-gray-700">
            Enable real-time streaming results
          </label>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSearching || !query.trim() || selectedSources.length === 0}
          className="w-full flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSearching ? (
            <>
              <Loader2 className="animate-spin h-5 w-5 mr-2" />
              Searching...
            </>
          ) : (
            <>
              <Search className="h-5 w-5 mr-2" />
              Search
            </>
          )}
        </button>
      </form>
    </div>
  )
}
