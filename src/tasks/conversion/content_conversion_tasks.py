"""Content conversion tasks for handling different content types between APIs."""

from typing import Any, Dict, List, Optional
from ...core.logging_config import get_logger

logger = get_logger("conversion.content")


def convert_image_content_anthropic_to_openai(image_block: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Anthropic image content block to OpenAI image_url format.
    
    Anthropic format:
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "base64_data_here"
        }
    }
    
    OpenAI format:
    {
        "type": "image_url",
        "image_url": {
            "url": "data:image/jpeg;base64,base64_data_here"
        }
    }
    
    Args:
        image_block: Anthropic image content block
        
    Returns:
        OpenAI-formatted image content block
    """
    try:
        source = image_block.get("source", {})
        
        if source.get("type") == "base64":
            media_type = source.get("media_type", "image/jpeg")
            data = source.get("data", "")
            
            if not data:
                logger.warning("Empty image data in base64 source")
                return {"type": "text", "text": "[Empty image content]"}
            
            # Create data URL format
            data_url = f"data:{media_type};base64,{data}"
            
            logger.debug("Converting Anthropic image to OpenAI format",
                        media_type=media_type,
                        data_length=len(data))
            
            return {
                "type": "image_url",
                "image_url": {
                    "url": data_url
                }
            }
        
        else:
            logger.warning("Unsupported image source type",
                          source_type=source.get("type", "unknown"))
            return {"type": "text", "text": f"[Unsupported image source: {source.get('type', 'unknown')}]"}
    
    except Exception as e:
        logger.error("Failed to convert image content",
                    error=str(e),
                    image_block_keys=list(image_block.keys()) if isinstance(image_block, dict) else "invalid")
        return {"type": "text", "text": "[Image conversion failed]"}


def convert_image_content_openai_to_anthropic(image_block: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert OpenAI image_url format to Anthropic image content block.
    
    OpenAI format:
    {
        "type": "image_url",
        "image_url": {
            "url": "data:image/jpeg;base64,base64_data_here"
        }
    }
    
    Anthropic format:
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "base64_data_here"
        }
    }
    
    Args:
        image_block: OpenAI image content block
        
    Returns:
        Anthropic-formatted image content block
    """
    try:
        image_url_data = image_block.get("image_url", {})
        url = image_url_data.get("url", "")
        
        if not url:
            logger.warning("Empty image URL in OpenAI image block")
            return {"type": "text", "text": "[Empty image URL]"}
        
        # Parse data URL format: data:media_type;base64,data
        if url.startswith("data:"):
            try:
                # Split data URL: data:image/jpeg;base64,actualdata
                header, data = url.split(",", 1)
                media_info = header.replace("data:", "").split(";")
                media_type = media_info[0] if media_info else "image/jpeg"
                
                logger.debug("Converting OpenAI image to Anthropic format",
                            media_type=media_type,
                            data_length=len(data))
                
                return {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": data
                    }
                }
            
            except ValueError as e:
                logger.error("Failed to parse data URL",
                            url_prefix=url[:50],
                            error=str(e))
                return {"type": "text", "text": "[Invalid image data URL]"}
        
        else:
            logger.warning("Non-data URL image not supported for Anthropic conversion",
                          url_prefix=url[:50])
            return {"type": "text", "text": f"[External image URL not supported: {url[:50]}...]"}
    
    except Exception as e:
        logger.error("Failed to convert OpenAI image content",
                    error=str(e),
                    image_block_keys=list(image_block.keys()) if isinstance(image_block, dict) else "invalid")
        return {"type": "text", "text": "[Image conversion failed]"}


def convert_content_blocks_anthropic_to_openai(content_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert a list of Anthropic content blocks to OpenAI format.
    
    Args:
        content_blocks: List of Anthropic content blocks
        
    Returns:
        List of OpenAI-formatted content blocks
    """
    converted_blocks = []
    
    for block in content_blocks:
        block_type = block.get("type", "unknown")
        
        if block_type == "text":
            # Text blocks remain the same
            converted_blocks.append(block)
        
        elif block_type == "image":
            # Convert image blocks
            converted_image = convert_image_content_anthropic_to_openai(block)
            converted_blocks.append(converted_image)
        
        elif block_type == "tool_use":
            # Tool use blocks need special handling - convert to text for now
            tool_name = block.get("name", "unknown_tool")
            tool_input = block.get("input", {})
            converted_blocks.append({
                "type": "text",
                "text": f"[Tool use: {tool_name} with input {tool_input}]"
            })
            logger.debug("Converted tool_use block to text representation",
                        tool_name=tool_name)
        
        elif block_type == "tool_result":
            # Tool result blocks - convert to text
            tool_use_id = block.get("tool_use_id", "unknown")
            content = block.get("content", "")
            converted_blocks.append({
                "type": "text", 
                "text": f"[Tool result for {tool_use_id}: {content}]"
            })
            logger.debug("Converted tool_result block to text representation",
                        tool_use_id=tool_use_id)
        
        else:
            logger.warning("Unknown content block type",
                          block_type=block_type)
            converted_blocks.append({
                "type": "text",
                "text": f"[Unsupported content type: {block_type}]"
            })
    
    return converted_blocks


def convert_content_blocks_openai_to_anthropic(content_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert a list of OpenAI content blocks to Anthropic format.
    
    Args:
        content_blocks: List of OpenAI content blocks
        
    Returns:
        List of Anthropic-formatted content blocks
    """
    converted_blocks = []
    
    for block in content_blocks:
        block_type = block.get("type", "unknown")
        
        if block_type == "text":
            # Text blocks remain the same
            converted_blocks.append(block)
        
        elif block_type == "image_url":
            # Convert image blocks
            converted_image = convert_image_content_openai_to_anthropic(block)
            converted_blocks.append(converted_image)
        
        else:
            logger.warning("Unknown OpenAI content block type",
                          block_type=block_type)
            converted_blocks.append({
                "type": "text",
                "text": f"[Unsupported OpenAI content type: {block_type}]"
            })
    
    return converted_blocks 