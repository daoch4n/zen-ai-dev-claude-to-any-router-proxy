"""Web operation Prefect tasks for OpenRouter Anthropic Server.

Converts WebToolExecutor methods into modular Prefect tasks.
Part of Phase 6A comprehensive refactoring - Task-per-Tool Architecture.
"""

import re
import time
from typing import Any, Dict, List
from urllib.parse import urlparse

from prefect import task

from ...services.tool_execution import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager

# Initialize logging and context management
logger = get_logger("web_tools")
context_manager = ContextManager()


class URLValidator:
    """Security validation for web URLs"""
    
    BLOCKED_SCHEMES = ['file', 'ftp', 'mailto', 'javascript']
    BLOCKED_DOMAINS = ['localhost', '127.0.0.1', '0.0.0.0']
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL for security issues"""
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme.lower() in URLValidator.BLOCKED_SCHEMES:
                logger.warning("Blocked URL scheme detected", scheme=parsed.scheme, url=url)
                return False
            
            # Only allow http/https
            if parsed.scheme.lower() not in ['http', 'https']:
                logger.warning("Non-HTTP URL scheme", scheme=parsed.scheme, url=url)
                return False
            
            # Check for blocked domains
            hostname = parsed.hostname
            if hostname and hostname.lower() in URLValidator.BLOCKED_DOMAINS:
                logger.warning("Blocked domain detected", domain=hostname, url=url)
                return False
            
            return True
            
        except Exception as e:
            logger.warning("Invalid URL format", url=url, error=str(e))
            return False


@task(name="web_search", retries=2, retry_delay_seconds=2)
async def web_search_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic web search operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (WebSearch)
        tool_input: Dictionary containing query and optional domain filters
    
    Returns:
        ToolExecutionResult with search results or error
    """
    start_time = time.time()
    
    # Create tool context for structured logging
    context_manager.create_tool_context(
        tool_name=tool_name,
        tool_call_id=tool_call_id,
        input_data=tool_input,
        execution_step=1
    )
    
    try:
        query = tool_input.get('query')
        allowed_domains = tool_input.get('allowed_domains', [])
        blocked_domains = tool_input.get('blocked_domains', [])
        
        if not query:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameter: query",
                execution_time=time.time() - start_time
            )
        
        # Import httpx here to avoid dependency issues if not installed
        try:
            import httpx
        except ImportError:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="httpx library not installed. Install with: pip install httpx",
                execution_time=time.time() - start_time
            )
        
        # Use DuckDuckGo HTML version for simple scraping
        search_url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(search_url, data=params)
            response.raise_for_status()
        
        # Parse results with basic HTML parsing
        results = []
        content = response.text
        
        # Simple regex-based extraction for DuckDuckGo HTML results
        # This is basic but avoids BeautifulSoup dependency
        result_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>'
        snippet_pattern = r'<a class="result__snippet" href="[^"]+">([^<]+)</a>'
        
        urls = re.findall(result_pattern, content)
        snippets = re.findall(snippet_pattern, content)
        
        for i, (url, title) in enumerate(urls[:10]):  # Limit to 10 results
            # Apply domain filtering
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
            except:
                domain = ''
            
            if allowed_domains and not any(allowed.lower() in domain for allowed in allowed_domains):
                continue
                
            if blocked_domains and any(blocked.lower() in domain for blocked in blocked_domains):
                continue
            
            snippet = snippets[i] if i < len(snippets) else ''
            # Clean up HTML entities
            title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            snippet = snippet.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            
            results.append({
                'title': title.strip(),
                'url': url,
                'snippet': snippet.strip()
            })
        
        if not results:
            result_content = "No search results found"
        else:
            result_lines = []
            for i, result in enumerate(results, 1):
                result_lines.append(f"{i}. {result['title']}")
                result_lines.append(f"   URL: {result['url']}")
                if result['snippet']:
                    result_lines.append(f"   {result['snippet']}")
                result_lines.append("")
            result_content = "\n".join(result_lines)
        
        logger.info("WebSearch tool executed successfully",
                   query=query,
                   result_count=len(results),
                   allowed_domains=allowed_domains,
                   blocked_domains=blocked_domains,
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=result_content,
            execution_time=time.time() - start_time
        )
        
    except Exception as e:
        error_msg = f"Failed to execute web search for '{query}': {e}"
        logger.error("WebSearch tool execution failed",
                    query=query,
                    error=str(e),
                    tool_call_id=tool_call_id,
                    exc_info=True)
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=error_msg,
            execution_time=time.time() - start_time
        )


@task(name="web_fetch", retries=2, retry_delay_seconds=2)
async def web_fetch_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic web fetch operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (WebFetch)
        tool_input: Dictionary containing url and optional parameters
    
    Returns:
        ToolExecutionResult with page content or error
    """
    start_time = time.time()
    
    # Create tool context for structured logging
    context_manager.create_tool_context(
        tool_name=tool_name,
        tool_call_id=tool_call_id,
        input_data=tool_input,
        execution_step=1
    )
    
    try:
        url = tool_input.get('url')
        max_length = tool_input.get('max_length', 50000)  # Default 50KB limit
        
        if not url:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameter: url",
                execution_time=time.time() - start_time
            )
        
        # Validate URL for security
        if not URLValidator.validate_url(url):
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Invalid or blocked URL: {url}",
                execution_time=time.time() - start_time
            )
        
        # Import httpx here to avoid dependency issues if not installed
        try:
            import httpx
        except ImportError:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="httpx library not installed. Install with: pip install httpx",
                execution_time=time.time() - start_time
            )
        
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Claude-Code-Assistant/1.0)'
        }
        
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(ct in content_type for ct in ['text/', 'application/json', 'application/xml']):
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"Unsupported content type: {content_type}",
                    execution_time=time.time() - start_time
                )
            
            # Get content and apply length limit
            content = response.text
            original_length = len(content)
            
            if len(content) > max_length:
                content = content[:max_length]
                truncated = True
            else:
                truncated = False
            
            # Basic content cleaning for HTML
            if 'html' in content_type:
                # Remove script and style tags
                content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
                content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
                
                # Remove HTML tags for cleaner text (optional basic cleaning)
                # This is very basic - for better HTML parsing, would need BeautifulSoup
                clean_content = re.sub(r'<[^>]+>', '', content)
                clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                
                # Use cleaned content if significantly shorter (indicates successful tag removal)
                if len(clean_content) < len(content) * 0.8:
                    content = clean_content
            
            # Format result
            result_lines = [
                f"Successfully fetched: {url}",
                f"Content-Type: {content_type}",
                f"Content-Length: {original_length} chars" + (" (truncated)" if truncated else ""),
                "",
                "Content:",
                content
            ]
            result_content = "\n".join(result_lines)
            
            logger.info("WebFetch tool executed successfully",
                       url=url,
                       content_type=content_type,
                       content_length=original_length,
                       truncated=truncated,
                       tool_call_id=tool_call_id)
            
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=True,
                result=result_content,
                execution_time=time.time() - start_time
            )
        
    except httpx.TimeoutException:
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=f"Request timeout while fetching: {url}",
            execution_time=time.time() - start_time
        )
    except httpx.HTTPStatusError as e:
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=f"HTTP {e.response.status_code} error fetching {url}: {e.response.text[:200]}",
            execution_time=time.time() - start_time
        )
    except Exception as e:
        error_msg = f"Failed to fetch URL '{url}': {e}"
        logger.error("WebFetch tool execution failed",
                    url=url,
                    error=str(e),
                    tool_call_id=tool_call_id,
                    exc_info=True)
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=error_msg,
            execution_time=time.time() - start_time
        )