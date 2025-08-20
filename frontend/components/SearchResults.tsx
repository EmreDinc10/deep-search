'use client'

import { useState } from 'react'
import { ExternalLink, Clock, TrendingUp, Sparkles } from 'lucide-react'

interface SearchResult {
  source: string
  title: string
  url: string
  snippet: string
  timestamp?: string
  score?: number
}

interface SearchResponse {
  query: string
  results: Record<string, SearchResult[]>
  ai_synthesis?: string
  search_duration: number
  total_results: number
}

interface SearchResultsProps {
  response: SearchResponse
}

const sourceColors: Record<string, string> = {
  google: 'bg-blue-500',
  duckduckgo: 'bg-orange-500',
  wikipedia: 'bg-gray-600',
  reddit: 'bg-red-500',
}

const sourceNames: Record<string, string> = {
  google: 'Google',
  duckduckgo: 'DuckDuckGo',
  wikipedia: 'Wikipedia',
  reddit: 'Reddit',
}

export default function SearchResults({ response }: SearchResultsProps) {
  const [activeTab, setActiveTab] = useState<string>('overview')

  const sourcesWithResults = Object.entries(response.results).filter(([_, results]) => results.length > 0)

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gray-50 px-6 py-4 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Search Results</h2>
            <p className="text-sm text-gray-600 mt-1">
              Found {response.total_results} results in {response.search_duration.toFixed(2)}s
            </p>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            <span>{response.search_duration.toFixed(2)}s</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex space-x-8 px-6" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <TrendingUp className="w-4 h-4 mr-2" />
              Overview
            </div>
          </button>
          
          {response.ai_synthesis && (
            <button
              onClick={() => setActiveTab('ai-synthesis')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'ai-synthesis'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center">
                <Sparkles className="w-4 h-4 mr-2" />
                AI Synthesis
              </div>
            </button>
          )}

          {sourcesWithResults.map(([source, _]) => (
            <button
              key={source}
              onClick={() => setActiveTab(source)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === source
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded mr-2 ${sourceColors[source] || 'bg-gray-400'}`}></div>
                {sourceNames[source] || source} ({response.results[source]?.length || 0})
              </div>
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-600">{response.total_results}</div>
                <div className="text-sm text-blue-800">Total Results</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-600">{sourcesWithResults.length}</div>
                <div className="text-sm text-green-800">Active Sources</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-600">{response.search_duration.toFixed(1)}s</div>
                <div className="text-sm text-purple-800">Search Duration</div>
              </div>
            </div>

            {/* Results by Source */}
            <div className="space-y-4">
              {sourcesWithResults.map(([source, results]) => (
                <div key={source} className="border rounded-lg p-4">
                  <div className="flex items-center mb-3">
                    <div className={`w-4 h-4 rounded mr-3 ${sourceColors[source] || 'bg-gray-400'}`}></div>
                    <h3 className="font-semibold text-gray-900">{sourceNames[source] || source}</h3>
                    <span className="ml-2 text-sm text-gray-500">({results.length} results)</span>
                  </div>
                  <div className="space-y-2">
                    {results.slice(0, 3).map((result, index) => (
                      <div key={index} className="text-sm">
                        <a
                          href={result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary-600 hover:text-primary-800 font-medium flex items-center"
                        >
                          {result.title}
                          <ExternalLink className="w-3 h-3 ml-1" />
                        </a>
                        <p className="text-gray-600 mt-1 line-clamp-2">{result.snippet}</p>
                      </div>
                    ))}
                    {results.length > 3 && (
                      <button
                        onClick={() => setActiveTab(source)}
                        className="text-sm text-primary-600 hover:text-primary-800"
                      >
                        View all {results.length} results...
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'ai-synthesis' && response.ai_synthesis && (
          <div className="prose max-w-none">
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Sparkles className="w-5 h-5 text-purple-600 mr-2" />
                <h3 className="text-lg font-semibold text-gray-900">AI Synthesis</h3>
              </div>
              <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                {response.ai_synthesis}
              </div>
            </div>
          </div>
        )}

        {sourcesWithResults.map(([source, results]) => (
          activeTab === source && (
            <div key={source} className="space-y-4">
              <div className="flex items-center mb-4">
                <div className={`w-5 h-5 rounded mr-3 ${sourceColors[source] || 'bg-gray-400'}`}></div>
                <h3 className="text-lg font-semibold text-gray-900">{sourceNames[source] || source} Results</h3>
                <span className="ml-2 text-sm text-gray-500">({results.length} results)</span>
              </div>
              {results.map((result, index) => (
                <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0">
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-lg font-medium text-primary-600 hover:text-primary-800 flex items-center mb-2"
                  >
                    {result.title}
                    <ExternalLink className="w-4 h-4 ml-2" />
                  </a>
                  <p className="text-gray-700 mb-2 leading-relaxed">{result.snippet}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span className="truncate">{result.url}</span>
                    {result.score && (
                      <span className="flex items-center">
                        <TrendingUp className="w-3 h-3 mr-1" />
                        Score: {result.score}
                      </span>
                    )}
                    {result.timestamp && (
                      <span className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {result.timestamp}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )
        ))}
      </div>
    </div>
  )
}
