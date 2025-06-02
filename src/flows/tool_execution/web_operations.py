"""Web operation flows for OpenRouter Anthropic Server.

Orchestrates web tool tasks with rate limiting and concurrent execution.
Part of Phase 6A comprehensive refactoring - Tool Execution Workflows.
"""

import asyncio
from typing import Any, Dict, List

from prefect import flow

from ...tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager
from ...tasks.tools.web_tools import (
    web_search_task,
    web_fetch_task
)

# Initialize logging and context management
logger = get_logger("web_operations")
context_manager = ContextManager()


@flow(name="web_operations")
async def web_operations_flow(
    tool_requests: List[Dict[str, Any]]
) -> List[ToolExecutionResult]:
    """
    Orchestrate web operations with rate limiting and concurrency.
    
    Strategy:
    - Search operations can run concurrently (different queries)
    - Fetch operations have limited concurrency (respect rate limits)
    - Mixed operations use semaphore to control total concurrent requests
    
    Args:
        tool_requests: List of tool request dictionaries
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting web operations flow", 
               request_count=len(tool_requests))
    
    # Categorize operations by type
    search_operations = []
    fetch_operations = []
    
    for request in tool_requests:
        tool_name = request.get('name', '').lower()
        if tool_name == 'websearch':
            search_operations.append(request)
        elif tool_name == 'webfetch':
            fetch_operations.append(request)
    
    results = []
    
    # Control concurrency to avoid overwhelming web services
    # Max 3 concurrent web operations to be respectful
    semaphore = asyncio.Semaphore(3)
    
    async def limited_web_search(request):
        async with semaphore:
            return await web_search_task(
                tool_call_id=request.get('tool_call_id'),
                tool_name=request.get('name'),
                tool_input=request.get('input', {})
            )
    
    async def limited_web_fetch(request):
        async with semaphore:
            return await web_fetch_task(
                tool_call_id=request.get('tool_call_id'),
                tool_name=request.get('name'),
                tool_input=request.get('input', {})
            )
    
    # Create all tasks with rate limiting
    all_tasks = []
    
    # Add search tasks
    for request in search_operations:
        task = limited_web_search(request)
        all_tasks.append(task)
    
    # Add fetch tasks
    for request in fetch_operations:
        task = limited_web_fetch(request)
        all_tasks.append(task)
    
    # Execute all web operations with controlled concurrency
    if all_tasks:
        logger.info("Executing web operations with rate limiting", 
                   total_tasks=len(all_tasks),
                   search_count=len(search_operations),
                   fetch_count=len(fetch_operations),
                   max_concurrent=3)
        
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
    
    successful_operations = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Web operations flow completed", 
               total_operations=len(tool_requests),
               successful_operations=successful_operations)
    
    return results


@flow(name="concurrent_web_search")
async def concurrent_web_search_flow(
    search_queries: List[str],
    base_tool_call_id: str,
    max_results_per_query: int = 10,
    max_concurrent_searches: int = 3
) -> List[ToolExecutionResult]:
    """
    Perform multiple web searches concurrently with rate limiting.
    
    Args:
        search_queries: List of search queries
        base_tool_call_id: Base ID for generating unique tool call IDs
        max_results_per_query: Maximum results per search
        max_concurrent_searches: Maximum concurrent searches
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting concurrent web search", 
               query_count=len(search_queries),
               max_concurrent=max_concurrent_searches)
    
    # Control concurrency for web searches
    semaphore = asyncio.Semaphore(max_concurrent_searches)
    
    async def limited_search(query: str, index: int):
        async with semaphore:
            tool_call_id = f"{base_tool_call_id}_search_{index}"
            return await web_search_task(
                tool_call_id=tool_call_id,
                tool_name="WebSearch",
                tool_input={
                    "query": query,
                    "max_results": max_results_per_query
                }
            )
    
    # Create search tasks
    search_tasks = [
        limited_search(query, i) 
        for i, query in enumerate(search_queries)
    ]
    
    # Execute all searches concurrently
    results = await asyncio.gather(*search_tasks, return_exceptions=True)
    
    successful_searches = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Concurrent web search completed", 
               total_queries=len(search_queries),
               successful_searches=successful_searches)
    
    return results


@flow(name="web_content_pipeline")
async def web_content_pipeline_flow(
    search_query: str,
    max_search_results: int,
    max_fetch_urls: int,
    base_tool_call_id: str
) -> Dict[str, ToolExecutionResult]:
    """
    Search web and then fetch content from top results.
    
    Args:
        search_query: Query to search for
        max_search_results: Maximum search results to retrieve
        max_fetch_urls: Maximum URLs to fetch content from
        base_tool_call_id: Base ID for generating unique tool call IDs
    
    Returns:
        Dictionary with search and fetch results
    """
    logger.info("Starting web content pipeline", 
               query=search_query,
               max_search_results=max_search_results,
               max_fetch_urls=max_fetch_urls)
    
    # Step 1: Perform web search
    search_result = await web_search_task(
        tool_call_id=f"{base_tool_call_id}_search",
        tool_name="WebSearch",
        tool_input={
            "query": search_query,
            "max_results": max_search_results
        }
    )
    
    fetch_results = []
    
    # Step 2: Extract URLs from search results and fetch content
    if search_result.success and search_result.content:
        try:
            # Parse search results to extract URLs
            search_content = search_result.content
            urls = []
            
            # Simple URL extraction from search results
            # This is a basic implementation - could be enhanced
            if isinstance(search_content, str):
                import re
                url_pattern = r'https?://[^\s<>"]+[^\s<>",.]'
                found_urls = re.findall(url_pattern, search_content)
                urls = found_urls[:max_fetch_urls]
            
            if urls:
                # Control concurrency for fetches (max 2 concurrent)
                semaphore = asyncio.Semaphore(2)
                
                async def limited_fetch(url: str, index: int):
                    async with semaphore:
                        tool_call_id = f"{base_tool_call_id}_fetch_{index}"
                        return await web_fetch_task(
                            tool_call_id=tool_call_id,
                            tool_name="WebFetch",
                            tool_input={"url": url}
                        )
                
                # Create fetch tasks
                fetch_tasks = [
                    limited_fetch(url, i) 
                    for i, url in enumerate(urls)
                ]
                
                # Execute fetches concurrently
                logger.info("Fetching content from URLs", 
                           url_count=len(urls))
                
                fetch_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
        
        except Exception as e:
            logger.error("Error in web content pipeline", 
                        error=str(e), 
                        search_success=search_result.success)
    
    successful_fetches = sum(1 for r in fetch_results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Web content pipeline completed", 
               search_success=search_result.success,
               successful_fetches=successful_fetches,
               total_fetch_attempts=len(fetch_results))
    
    return {
        "search_result": search_result,
        "fetch_results": fetch_results
    }


@flow(name="batch_url_fetch")
async def batch_url_fetch_flow(
    urls: List[str],
    base_tool_call_id: str,
    max_concurrent_fetches: int = 2
) -> List[ToolExecutionResult]:
    """
    Fetch content from multiple URLs concurrently with rate limiting.
    
    Args:
        urls: List of URLs to fetch
        base_tool_call_id: Base ID for generating unique tool call IDs
        max_concurrent_fetches: Maximum concurrent fetch operations
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting batch URL fetch", 
               url_count=len(urls),
               max_concurrent=max_concurrent_fetches)
    
    # Control concurrency for fetches
    semaphore = asyncio.Semaphore(max_concurrent_fetches)
    
    async def limited_fetch(url: str, index: int):
        async with semaphore:
            tool_call_id = f"{base_tool_call_id}_fetch_{index}"
            return await web_fetch_task(
                tool_call_id=tool_call_id,
                tool_name="WebFetch",
                tool_input={"url": url}
            )
    
    # Create fetch tasks
    fetch_tasks = [
        limited_fetch(url, i) 
        for i, url in enumerate(urls)
    ]
    
    # Execute all fetches concurrently
    results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
    
    successful_fetches = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Batch URL fetch completed", 
               total_urls=len(urls),
               successful_fetches=successful_fetches)
    
    return results


@flow(name="web_research")
async def web_research_flow(
    research_topics: List[str],
    base_tool_call_id: str,
    results_per_topic: int = 5,
    urls_to_fetch_per_topic: int = 2
) -> Dict[str, Dict[str, Any]]:
    """
    Comprehensive web research on multiple topics.
    
    Args:
        research_topics: List of topics to research
        base_tool_call_id: Base ID for generating unique tool call IDs
        results_per_topic: Search results per topic
        urls_to_fetch_per_topic: URLs to fetch content from per topic
    
    Returns:
        Dictionary mapping topics to their research results
    """
    logger.info("Starting comprehensive web research", 
               topic_count=len(research_topics),
               results_per_topic=results_per_topic,
               urls_per_topic=urls_to_fetch_per_topic)
    
    # Control concurrency across all research operations
    semaphore = asyncio.Semaphore(2)  # Conservative limit for respectful web usage
    
    async def research_topic(topic: str, index: int):
        async with semaphore:
            topic_tool_call_id = f"{base_tool_call_id}_research_{index}"
            
            # Use the web content pipeline for each topic
            pipeline_result = await web_content_pipeline_flow(
                search_query=topic,
                max_search_results=results_per_topic,
                max_fetch_urls=urls_to_fetch_per_topic,
                base_tool_call_id=topic_tool_call_id
            )
            
            return {
                "topic": topic,
                "search_result": pipeline_result["search_result"],
                "fetch_results": pipeline_result["fetch_results"]
            }
    
    # Create research tasks for each topic
    research_tasks = [
        research_topic(topic, i) 
        for i, topic in enumerate(research_topics)
    ]
    
    # Execute all research concurrently
    research_results = await asyncio.gather(*research_tasks, return_exceptions=True)
    
    # Organize results by topic
    topic_results = {}
    successful_research = 0
    
    for result in research_results:
        if isinstance(result, dict) and "topic" in result:
            topic = result["topic"]
            topic_results[topic] = {
                "search_result": result["search_result"],
                "fetch_results": result["fetch_results"]
            }
            
            # Count success
            search_success = result["search_result"].success if hasattr(result["search_result"], 'success') else False
            fetch_successes = sum(1 for r in result["fetch_results"] 
                                if isinstance(r, ToolExecutionResult) and r.success)
            
            if search_success or fetch_successes > 0:
                successful_research += 1
            
            logger.debug("Topic research summary", 
                        topic=topic,
                        search_success=search_success,
                        successful_fetches=fetch_successes)
        else:
            logger.error("Research task failed", 
                        result_type=type(result).__name__)
    
    logger.info("Web research flow completed", 
               total_topics=len(research_topics),
               successful_research=successful_research)
    
    return topic_results


@flow(name="url_validation_and_fetch")
async def url_validation_and_fetch_flow(
    urls: List[str],
    base_tool_call_id: str,
    validate_before_fetch: bool = True
) -> Dict[str, List[ToolExecutionResult]]:
    """
    Validate URLs and fetch content only from valid ones.
    
    Args:
        urls: List of URLs to validate and fetch
        base_tool_call_id: Base ID for generating unique tool call IDs
        validate_before_fetch: Whether to validate URLs before fetching
    
    Returns:
        Dictionary with validation and fetch results
    """
    logger.info("Starting URL validation and fetch", 
               url_count=len(urls),
               validate_first=validate_before_fetch)
    
    if validate_before_fetch:
        # Simple URL validation (could be enhanced with actual HTTP HEAD requests)
        import re
        url_pattern = r'^https?://[^\s<>"]+[^\s<>",.]$'
        valid_urls = [url for url in urls if re.match(url_pattern, url)]
        invalid_urls = [url for url in urls if not re.match(url_pattern, url)]
        
        logger.info("URL validation completed", 
                   total_urls=len(urls),
                   valid_urls=len(valid_urls),
                   invalid_urls=len(invalid_urls))
        
        if invalid_urls:
            logger.warning("Invalid URLs found", invalid_urls=invalid_urls)
    else:
        valid_urls = urls
        invalid_urls = []
    
    # Fetch content from valid URLs
    fetch_results = []
    if valid_urls:
        fetch_results = await batch_url_fetch_flow(
            urls=valid_urls,
            base_tool_call_id=base_tool_call_id,
            max_concurrent_fetches=2
        )
    
    successful_fetches = sum(1 for r in fetch_results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("URL validation and fetch completed", 
               valid_urls=len(valid_urls),
               successful_fetches=successful_fetches)
    
    return {
        "valid_urls": valid_urls,
        "invalid_urls": invalid_urls,
        "fetch_results": fetch_results
    }