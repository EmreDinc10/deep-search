import os
from typing import List, Dict
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

from models import SearchResult, SearchSource

# Load environment variables
load_dotenv()

class AzureOpenAIClient:
    """Azure OpenAI client for synthesizing search results"""
    
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "o3-mini")
    
    async def synthesize_results(self, query: str, results: Dict[SearchSource, List[SearchResult]]) -> str:
        """Synthesize search results using Azure OpenAI"""
        
        # Format results for the AI
        formatted_results = self._format_results_for_ai(results)
        
        system_prompt = """
        You are an expert research assistant. Your task is to analyze and synthesize information from multiple search sources to provide a comprehensive, well-structured response to the user's query.

        Guidelines:
        1. Provide a clear, comprehensive answer based on the search results
        2. Cite sources when making specific claims
        3. Identify patterns and connections across different sources
        4. Highlight any conflicting information found
        5. Structure your response with clear sections if appropriate
        6. Be objective and factual
        7. If information is limited, acknowledge the limitations
        
        Format your response in a clear, readable manner with proper sections and bullet points where appropriate.
        """
        
        user_prompt = f"""
        Query: {query}
        
        Search Results from Multiple Sources:
        {formatted_results}
        
        Please analyze and synthesize this information to provide a comprehensive answer to the query. Include insights from the different sources and identify key themes or patterns.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_completion_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error synthesizing results: {str(e)}"
    
    def _format_results_for_ai(self, results: Dict[SearchSource, List[SearchResult]]) -> str:
        """Format search results for AI processing"""
        formatted = []
        
        for source, source_results in results.items():
            if source_results:
                formatted.append(f"\n=== {source.value.upper()} RESULTS ===")
                for i, result in enumerate(source_results[:5], 1):  # Limit to top 5 per source
                    formatted.append(f"\n{i}. Title: {result.title}")
                    formatted.append(f"   URL: {result.url}")
                    formatted.append(f"   Content: {result.snippet}")
                    if result.score:
                        formatted.append(f"   Score: {result.score}")
            else:
                formatted.append(f"\n=== {source.value.upper()} RESULTS ===")
                formatted.append("No results found")
        
        return "\n".join(formatted)
    
    async def generate_search_insights(self, query: str, results: Dict[SearchSource, List[SearchResult]]) -> Dict[str, str]:
        """Generate insights about the search results"""
        
        total_results = sum(len(source_results) for source_results in results.values())
        sources_with_results = [source.value for source, source_results in results.items() if source_results]
        
        insights = {
            "total_results": str(total_results),
            "sources_with_results": ", ".join(sources_with_results),
            "coverage": f"{len(sources_with_results)}/{len(results)} sources returned results"
        }
        
        # Generate AI-powered insights about result quality and relevance
        if total_results > 0:
            insight_prompt = f"""
            Analyze these search results for the query "{query}" and provide brief insights about:
            1. Result quality and relevance
            2. Information diversity across sources
            3. Any notable patterns or themes
            
            Keep response under 200 words.
            
            {self._format_results_for_ai(results)}
            """
            
            try:
                response = await self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[
                        {"role": "user", "content": insight_prompt}
                    ],
                    temperature=0.5,
                    max_completion_tokens=300
                )
                
                insights["ai_analysis"] = response.choices[0].message.content
            except Exception as e:
                insights["ai_analysis"] = f"Error generating insights: {str(e)}"
        else:
            insights["ai_analysis"] = "No results found to analyze"
        
        return insights
