"""Security Validation Tasks for OpenRouter Anthropic Server.

Prefect tasks for validating security aspects of requests, content safety, and threat detection.
Part of Phase 6B comprehensive refactoring - Validation Tasks.
"""

import hashlib
import re
import time
from typing import Any, Dict, List, Optional, Set

from prefect import task

from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult

# Initialize logging
logger = get_logger("security_validation")


@task(
    name="validate_content_safety",
    description="Validate content for safety and policy compliance",
    tags=["validation", "security", "content-safety"]
)
async def validate_content_safety_task(
    content: str,
    safety_rules: Dict[str, Any] = None,
    validation_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate content for safety, policy compliance, and harmful patterns.
    
    Args:
        content: Content to validate for safety
        safety_rules: Safety validation rules and thresholds
        validation_options: Optional validation configuration
    
    Returns:
        ConversionResult with safety validation status and details
    """
    logger.info("Validating content safety", content_length=len(content))
    
    try:
        if safety_rules is None:
            safety_rules = {}
        if validation_options is None:
            validation_options = {}
        
        validation_result = {
            "is_safe": True,
            "safety_score": 1.0,
            "violations": [],
            "warnings": [],
            "safety_analysis": {
                "content_length": len(content),
                "detected_patterns": [],
                "risk_categories": {},
                "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16]
            }
        }
        
        # Detect harmful patterns
        harmful_patterns = await _detect_harmful_patterns(content)
        if harmful_patterns["violations"]:
            validation_result["violations"].extend(harmful_patterns["violations"])
            validation_result["is_safe"] = False
        
        validation_result["warnings"].extend(harmful_patterns["warnings"])
        validation_result["safety_analysis"]["detected_patterns"] = harmful_patterns["patterns"]
        validation_result["safety_analysis"]["risk_categories"] = harmful_patterns["risk_categories"]
        
        # Calculate safety score
        base_score = 1.0
        violation_penalty = len(harmful_patterns["violations"]) * 0.2
        warning_penalty = len(harmful_patterns["warnings"]) * 0.05
        
        validation_result["safety_score"] = max(0.0, base_score - violation_penalty - warning_penalty)
        
        # Check against safety thresholds
        min_safety_score = safety_rules.get("min_safety_score", 0.7)
        if validation_result["safety_score"] < min_safety_score:
            validation_result["violations"].append(f"Safety score {validation_result['safety_score']:.2f} below threshold {min_safety_score}")
            validation_result["is_safe"] = False
        
        # Content length checks
        max_content_length = safety_rules.get("max_content_length", 100000)
        if len(content) > max_content_length:
            validation_result["warnings"].append(f"Content is very long ({len(content)} chars)")
        
        # PII detection
        if validation_options.get("check_pii", True):
            pii_detection = await _detect_pii_patterns(content)
            if pii_detection["found_pii"]:
                validation_result["warnings"].extend(pii_detection["warnings"])
                validation_result["safety_analysis"]["pii_detected"] = pii_detection["pii_types"]
        
        # Spam/promotional content detection
        if validation_options.get("check_spam", True):
            spam_detection = await _detect_spam_patterns(content)
            if spam_detection["is_spam"]:
                validation_result["warnings"].append("Content appears to be promotional/spam")
                validation_result["safety_analysis"]["spam_indicators"] = spam_detection["indicators"]
        
        logger.info("Content safety validation completed",
                   is_safe=validation_result["is_safe"],
                   safety_score=validation_result["safety_score"],
                   violation_count=len(validation_result["violations"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "safety_score": validation_result["safety_score"],
                "validation_type": "content_safety"
            }
        )
        
    except Exception as e:
        error_msg = f"Content safety validation failed: {str(e)}"
        logger.error("Content safety validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(
    name="validate_request_authentication",
    description="Validate request authentication and authorization",
    tags=["validation", "security", "auth"]
)
async def validate_request_authentication_task(
    auth_data: Dict[str, Any],
    auth_requirements: Dict[str, Any] = None,
    validation_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate request authentication and authorization.
    
    Args:
        auth_data: Authentication data from request
        auth_requirements: Authentication requirements and rules
        validation_options: Optional validation configuration
    
    Returns:
        ConversionResult with authentication validation status and details
    """
    logger.info("Validating request authentication")
    
    try:
        if auth_requirements is None:
            auth_requirements = {
                "require_api_key": True,
                "require_valid_format": True,
                "check_key_expiry": True,
                "check_permissions": True
            }
        
        if validation_options is None:
            validation_options = {}
        
        validation_result = {
            "is_authenticated": False,
            "is_authorized": False,
            "auth_method": None,
            "errors": [],
            "warnings": [],
            "auth_info": {
                "has_api_key": False,
                "has_bearer_token": False,
                "key_format_valid": False,
                "key_length": 0,
                "permissions": [],
                "rate_limit_tier": "default"
            }
        }
        
        # Check for API key
        api_key = auth_data.get("api_key") or auth_data.get("x_api_key")
        if api_key:
            validation_result["auth_info"]["has_api_key"] = True
            validation_result["auth_info"]["key_length"] = len(api_key)
            validation_result["auth_method"] = "api_key"
            
            # Validate API key format
            key_validation = await _validate_api_key_format(api_key)
            if key_validation["is_valid"]:
                validation_result["auth_info"]["key_format_valid"] = True
                validation_result["is_authenticated"] = True
            else:
                validation_result["errors"].extend(key_validation["errors"])
            
            validation_result["warnings"].extend(key_validation["warnings"])
        
        # Check for Bearer token
        bearer_token = auth_data.get("authorization")
        if bearer_token and bearer_token.startswith("Bearer "):
            validation_result["auth_info"]["has_bearer_token"] = True
            token = bearer_token[7:]  # Remove "Bearer " prefix
            
            if not api_key:  # Only use bearer if no API key
                validation_result["auth_method"] = "bearer_token"
                
                # Validate bearer token format
                token_validation = await _validate_bearer_token_format(token)
                if token_validation["is_valid"]:
                    validation_result["is_authenticated"] = True
                else:
                    validation_result["errors"].extend(token_validation["errors"])
                
                validation_result["warnings"].extend(token_validation["warnings"])
        
        # Check authentication requirements
        if auth_requirements["require_api_key"] and not validation_result["auth_info"]["has_api_key"]:
            validation_result["errors"].append("API key required but not provided")
        
        if not validation_result["is_authenticated"] and (validation_result["auth_info"]["has_api_key"] or validation_result["auth_info"]["has_bearer_token"]):
            validation_result["errors"].append("Authentication credentials provided but invalid")
        
        # Authorization checks (if authenticated)
        if validation_result["is_authenticated"]:
            auth_token = api_key or (bearer_token[7:] if bearer_token else None)
            
            if auth_token:
                # Check permissions (mock implementation)
                permissions = await _check_token_permissions(auth_token)
                validation_result["auth_info"]["permissions"] = permissions["permissions"]
                validation_result["auth_info"]["rate_limit_tier"] = permissions["rate_limit_tier"]
                
                if permissions["is_valid"]:
                    validation_result["is_authorized"] = True
                else:
                    validation_result["errors"].extend(permissions["errors"])
                
                validation_result["warnings"].extend(permissions["warnings"])
        
        # Security checks
        if validation_options.get("check_token_reuse", True):
            token_reuse_check = await _check_token_reuse(auth_data.get("api_key", ""))
            if token_reuse_check["suspicious"]:
                validation_result["warnings"].append("Possible token reuse detected")
        
        logger.info("Request authentication validation completed",
                   is_authenticated=validation_result["is_authenticated"],
                   is_authorized=validation_result["is_authorized"],
                   auth_method=validation_result["auth_method"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "auth_method": validation_result["auth_method"],
                "validation_type": "authentication"
            }
        )
        
    except Exception as e:
        error_msg = f"Authentication validation failed: {str(e)}"
        logger.error("Authentication validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(
    name="validate_request_origin",
    description="Validate request origin and detect suspicious sources",
    tags=["validation", "security", "origin"]
)
async def validate_request_origin_task(
    request_metadata: Dict[str, Any],
    origin_rules: Dict[str, Any] = None,
    validation_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate request origin and detect suspicious sources.
    
    Args:
        request_metadata: Request metadata including origin information
        origin_rules: Origin validation rules and restrictions
        validation_options: Optional validation configuration
    
    Returns:
        ConversionResult with origin validation status and details
    """
    logger.info("Validating request origin")
    
    try:
        if origin_rules is None:
            origin_rules = {
                "allowed_origins": [],
                "blocked_origins": [],
                "check_geolocation": True,
                "check_vpn": True,
                "rate_limit_suspicious": True
            }
        
        if validation_options is None:
            validation_options = {}
        
        validation_result = {
            "is_valid_origin": True,
            "is_suspicious": False,
            "risk_score": 0.0,
            "errors": [],
            "warnings": [],
            "origin_info": {
                "ip_address": request_metadata.get("client_ip"),
                "user_agent": request_metadata.get("user_agent"),
                "referer": request_metadata.get("referer"),
                "origin_header": request_metadata.get("origin"),
                "forwarded_for": request_metadata.get("x_forwarded_for"),
                "country": None,
                "is_vpn": False,
                "is_tor": False
            }
        }
        
        # Extract origin information
        client_ip = request_metadata.get("client_ip")
        user_agent = request_metadata.get("user_agent", "")
        origin_header = request_metadata.get("origin")
        
        # Validate IP address
        if client_ip:
            ip_validation = await _validate_ip_address(client_ip)
            validation_result["origin_info"].update(ip_validation["info"])
            
            if not ip_validation["is_valid"]:
                validation_result["errors"].extend(ip_validation["errors"])
                validation_result["is_valid_origin"] = False
            
            validation_result["warnings"].extend(ip_validation["warnings"])
            
            # Check if IP is in blocked list
            if client_ip in origin_rules.get("blocked_ips", []):
                validation_result["errors"].append(f"IP address {client_ip} is blocked")
                validation_result["is_valid_origin"] = False
        
        # Validate User-Agent
        if user_agent:
            ua_validation = await _validate_user_agent(user_agent)
            if ua_validation["is_suspicious"]:
                validation_result["is_suspicious"] = True
                validation_result["warnings"].extend(ua_validation["warnings"])
        
        # Validate Origin header
        if origin_header:
            # Check allowed origins
            allowed_origins = origin_rules.get("allowed_origins", [])
            if allowed_origins and origin_header not in allowed_origins:
                validation_result["warnings"].append(f"Origin {origin_header} not in allowed list")
            
            # Check blocked origins
            blocked_origins = origin_rules.get("blocked_origins", [])
            if origin_header in blocked_origins:
                validation_result["errors"].append(f"Origin {origin_header} is blocked")
                validation_result["is_valid_origin"] = False
        
        # Geolocation checks
        if origin_rules.get("check_geolocation", True) and client_ip:
            geo_info = await _check_ip_geolocation(client_ip)
            validation_result["origin_info"]["country"] = geo_info.get("country")
            
            # Check restricted countries
            restricted_countries = origin_rules.get("restricted_countries", [])
            if geo_info.get("country") in restricted_countries:
                validation_result["warnings"].append(f"Request from restricted country: {geo_info['country']}")
                validation_result["is_suspicious"] = True
        
        # VPN/Proxy detection
        if origin_rules.get("check_vpn", True) and client_ip:
            vpn_check = await _detect_vpn_proxy(client_ip)
            validation_result["origin_info"]["is_vpn"] = vpn_check["is_vpn"]
            validation_result["origin_info"]["is_tor"] = vpn_check["is_tor"]
            
            if vpn_check["is_vpn"]:
                validation_result["warnings"].append("Request appears to be from VPN/proxy")
                validation_result["is_suspicious"] = True
            
            if vpn_check["is_tor"]:
                validation_result["warnings"].append("Request appears to be from Tor network")
                validation_result["is_suspicious"] = True
        
        # Calculate risk score
        risk_factors = 0
        if validation_result["is_suspicious"]:
            risk_factors += 0.3
        if validation_result["origin_info"]["is_vpn"]:
            risk_factors += 0.2
        if validation_result["origin_info"]["is_tor"]:
            risk_factors += 0.4
        if not user_agent:
            risk_factors += 0.1
        
        validation_result["risk_score"] = min(1.0, risk_factors)
        
        # Check risk thresholds
        max_risk_score = validation_options.get("max_risk_score", 0.7)
        if validation_result["risk_score"] > max_risk_score:
            validation_result["errors"].append(f"Risk score {validation_result['risk_score']:.2f} exceeds threshold {max_risk_score}")
            validation_result["is_valid_origin"] = False
        
        logger.info("Request origin validation completed",
                   is_valid_origin=validation_result["is_valid_origin"],
                   is_suspicious=validation_result["is_suspicious"],
                   risk_score=validation_result["risk_score"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "risk_score": validation_result["risk_score"],
                "validation_type": "request_origin"
            }
        )
        
    except Exception as e:
        error_msg = f"Request origin validation failed: {str(e)}"
        logger.error("Request origin validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(
    name="validate_input_sanitization",
    description="Validate and sanitize user inputs for security",
    tags=["validation", "security", "sanitization"]
)
async def validate_input_sanitization_task(
    user_inputs: Dict[str, Any],
    sanitization_rules: Dict[str, Any] = None,
    validation_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate and sanitize user inputs for security vulnerabilities.
    
    Args:
        user_inputs: User input data to validate and sanitize
        sanitization_rules: Input sanitization rules and patterns
        validation_options: Optional validation configuration
    
    Returns:
        ConversionResult with sanitization status and cleaned data
    """
    logger.info("Validating input sanitization", input_count=len(user_inputs))
    
    try:
        if sanitization_rules is None:
            sanitization_rules = {
                "max_input_length": 10000,
                "strip_html": True,
                "check_sql_injection": True,
                "check_xss": True,
                "check_command_injection": True
            }
        
        if validation_options is None:
            validation_options = {}
        
        validation_result = {
            "is_safe": True,
            "sanitized_inputs": {},
            "security_violations": [],
            "warnings": [],
            "sanitization_info": {
                "total_inputs": len(user_inputs),
                "sanitized_count": 0,
                "violation_count": 0,
                "detected_threats": []
            }
        }
        
        # Process each input
        for input_name, input_value in user_inputs.items():
            input_result = await _sanitize_single_input(
                input_name, input_value, sanitization_rules
            )
            
            # Store sanitized value
            validation_result["sanitized_inputs"][input_name] = input_result["sanitized_value"]
            
            # Track violations
            if input_result["violations"]:
                validation_result["security_violations"].extend(
                    [f"Input '{input_name}': {violation}" for violation in input_result["violations"]]
                )
                validation_result["is_safe"] = False
                validation_result["sanitization_info"]["violation_count"] += len(input_result["violations"])
            
            # Track warnings
            validation_result["warnings"].extend(
                [f"Input '{input_name}': {warning}" for warning in input_result["warnings"]]
            )
            
            # Track detected threats
            validation_result["sanitization_info"]["detected_threats"].extend(input_result["threats"])
            
            # Track if input was sanitized
            if input_result["was_sanitized"]:
                validation_result["sanitization_info"]["sanitized_count"] += 1
        
        # Overall security assessment
        if validation_result["sanitization_info"]["violation_count"] > 5:
            validation_result["warnings"].append("Multiple security violations detected - possible attack attempt")
        
        # Check for coordinated attack patterns
        threat_analysis = await _analyze_threat_patterns(validation_result["sanitization_info"]["detected_threats"])
        if threat_analysis["is_coordinated_attack"]:
            validation_result["security_violations"].append("Coordinated attack pattern detected")
            validation_result["is_safe"] = False
        
        validation_result["warnings"].extend(threat_analysis["warnings"])
        
        logger.info("Input sanitization validation completed",
                   is_safe=validation_result["is_safe"],
                   sanitized_count=validation_result["sanitization_info"]["sanitized_count"],
                   violation_count=validation_result["sanitization_info"]["violation_count"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "sanitized_count": validation_result["sanitization_info"]["sanitized_count"],
                "validation_type": "input_sanitization"
            }
        )
        
    except Exception as e:
        error_msg = f"Input sanitization validation failed: {str(e)}"
        logger.error("Input sanitization validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


# Helper functions for security validation

async def _detect_harmful_patterns(content: str) -> Dict[str, Any]:
    """Detect harmful patterns in content."""
    result = {
        "violations": [],
        "warnings": [],
        "patterns": [],
        "risk_categories": {}
    }
    
    try:
        content_lower = content.lower()
        
        # Violence/harm patterns
        violence_patterns = [
            r'\b(kill|murder|violence|harm|hurt|attack|assault)\b',
            r'\b(weapon|gun|knife|bomb|explosive)\b',
            r'\b(suicide|self-harm|cutting)\b'
        ]
        
        violence_count = 0
        for pattern in violence_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                violence_count += len(matches)
                result["patterns"].extend(matches)
        
        if violence_count > 5:
            result["violations"].append("High frequency of violence-related content")
        elif violence_count > 0:
            result["warnings"].append(f"Violence-related content detected ({violence_count} instances)")
        
        result["risk_categories"]["violence"] = violence_count
        
        # Hate speech patterns
        hate_patterns = [
            r'\b(hate|racist|discrimination|bigot)\b',
            r'\b(nazi|hitler|genocide)\b'
        ]
        
        hate_count = 0
        for pattern in hate_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                hate_count += len(matches)
                result["patterns"].extend(matches)
        
        if hate_count > 2:
            result["violations"].append("Hate speech content detected")
        elif hate_count > 0:
            result["warnings"].append(f"Potential hate speech content ({hate_count} instances)")
        
        result["risk_categories"]["hate_speech"] = hate_count
        
        # Sexual content patterns
        sexual_patterns = [
            r'\b(sexual|explicit|adult|pornographic)\b',
            r'\b(nude|naked|sex)\b'
        ]
        
        sexual_count = 0
        for pattern in sexual_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                sexual_count += len(matches)
                result["patterns"].extend(matches)
        
        if sexual_count > 3:
            result["warnings"].append(f"Sexual content detected ({sexual_count} instances)")
        
        result["risk_categories"]["sexual"] = sexual_count
        
        # Illegal activity patterns
        illegal_patterns = [
            r'\b(drugs|cocaine|heroin|marijuana)\b',
            r'\b(illegal|criminal|fraud|scam)\b',
            r'\b(piracy|copyright|stolen)\b'
        ]
        
        illegal_count = 0
        for pattern in illegal_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                illegal_count += len(matches)
                result["patterns"].extend(matches)
        
        if illegal_count > 2:
            result["violations"].append("Illegal activity content detected")
        elif illegal_count > 0:
            result["warnings"].append(f"Potential illegal activity content ({illegal_count} instances)")
        
        result["risk_categories"]["illegal"] = illegal_count
        
    except Exception:
        result["warnings"].append("Error analyzing content patterns")
    
    return result


async def _detect_pii_patterns(content: str) -> Dict[str, Any]:
    """Detect personally identifiable information in content."""
    result = {
        "found_pii": False,
        "warnings": [],
        "pii_types": []
    }
    
    try:
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, content):
            result["found_pii"] = True
            result["warnings"].append("Email address detected")
            result["pii_types"].append("email")
        
        # Phone number patterns
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'
        if re.search(phone_pattern, content):
            result["found_pii"] = True
            result["warnings"].append("Phone number detected")
            result["pii_types"].append("phone")
        
        # Social Security Number patterns
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        if re.search(ssn_pattern, content):
            result["found_pii"] = True
            result["warnings"].append("Social Security Number detected")
            result["pii_types"].append("ssn")
        
        # Credit card patterns (simplified)
        cc_pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        if re.search(cc_pattern, content):
            result["found_pii"] = True
            result["warnings"].append("Credit card number detected")
            result["pii_types"].append("credit_card")
        
    except Exception:
        result["warnings"].append("Error detecting PII patterns")
    
    return result


async def _detect_spam_patterns(content: str) -> Dict[str, Any]:
    """Detect spam/promotional patterns in content."""
    result = {
        "is_spam": False,
        "indicators": []
    }
    
    try:
        content_lower = content.lower()
        
        # Spam indicators
        spam_phrases = [
            "click here", "buy now", "limited time", "act now",
            "free money", "guaranteed", "no risk", "earn money",
            "work from home", "lose weight", "miracle cure"
        ]
        
        spam_count = 0
        for phrase in spam_phrases:
            if phrase in content_lower:
                spam_count += 1
                result["indicators"].append(phrase)
        
        # Check for excessive capitalization
        if len(re.findall(r'[A-Z]{3,}', content)) > 5:
            spam_count += 1
            result["indicators"].append("excessive_caps")
        
        # Check for excessive exclamation marks
        if content.count('!') > 5:
            spam_count += 1
            result["indicators"].append("excessive_exclamation")
        
        # Check for repeated words
        words = content_lower.split()
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        repeated_words = sum(1 for count in word_counts.values() if count > 5)
        if repeated_words > 3:
            spam_count += 1
            result["indicators"].append("repeated_words")
        
        result["is_spam"] = spam_count >= 3
        
    except Exception:
        pass
    
    return result


async def _validate_api_key_format(api_key: str) -> Dict[str, Any]:
    """Validate API key format and structure."""
    result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Check length
        if len(api_key) < 20:
            result["errors"].append("API key too short")
            result["is_valid"] = False
        elif len(api_key) > 200:
            result["warnings"].append("API key is very long")
        
        # Check format patterns
        if api_key.startswith(("sk-", "pk-", "rk-")):
            # Standard API key format
            if not re.match(r'^[a-zA-Z0-9\-_]+$', api_key):
                result["errors"].append("API key contains invalid characters")
                result["is_valid"] = False
        else:
            result["warnings"].append("API key doesn't follow standard format")
        
        # Check for suspicious patterns
        if api_key.lower() in ["test", "demo", "example", "placeholder"]:
            result["errors"].append("API key appears to be a placeholder")
            result["is_valid"] = False
        
    except Exception:
        result["errors"].append("Error validating API key format")
        result["is_valid"] = False
    
    return result


async def _validate_bearer_token_format(token: str) -> Dict[str, Any]:
    """Validate Bearer token format and structure."""
    result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Check length
        if len(token) < 10:
            result["errors"].append("Bearer token too short")
            result["is_valid"] = False
        elif len(token) > 1000:
            result["warnings"].append("Bearer token is very long")
        
        # Check for JWT format
        parts = token.split('.')
        if len(parts) == 3:
            # Looks like JWT
            try:
                import base64
                import json
                
                # Try to decode header (basic validation)
                header_data = base64.urlsafe_b64decode(parts[0] + '==')
                header = json.loads(header_data)
                
                if 'alg' not in header:
                    result["warnings"].append("JWT header missing algorithm")
                
            except Exception:
                result["warnings"].append("Invalid JWT format")
        
        # Check for suspicious patterns
        if token.lower() in ["test", "demo", "example"]:
            result["errors"].append("Bearer token appears to be a placeholder")
            result["is_valid"] = False
        
    except Exception:
        result["errors"].append("Error validating Bearer token format")
        result["is_valid"] = False
    
    return result


async def _check_token_permissions(token: str) -> Dict[str, Any]:
    """Check token permissions and validity (mock implementation)."""
    result = {
        "is_valid": True,
        "permissions": [],
        "rate_limit_tier": "default",
        "errors": [],
        "warnings": []
    }
    
    try:
        # Mock permission checking based on token characteristics
        if token.startswith("sk-"):
            result["permissions"] = ["read", "write", "admin"]
            result["rate_limit_tier"] = "premium"
        elif token.startswith("pk-"):
            result["permissions"] = ["read"]
            result["rate_limit_tier"] = "basic"
        else:
            result["permissions"] = ["read", "write"]
            result["rate_limit_tier"] = "standard"
        
        # Check for demo/test tokens
        if "test" in token.lower() or "demo" in token.lower():
            result["rate_limit_tier"] = "demo"
            result["warnings"].append("Demo/test token detected")
        
    except Exception:
        result["errors"].append("Error checking token permissions")
        result["is_valid"] = False
    
    return result


async def _check_token_reuse(token: str) -> Dict[str, Any]:
    """Check for suspicious token reuse patterns."""
    result = {
        "suspicious": False,
        "reasons": []
    }
    
    try:
        # Mock implementation - would normally check against usage database
        # For now, just return safe defaults
        pass
        
    except Exception:
        pass
    
    return result


async def _validate_ip_address(ip_address: str) -> Dict[str, Any]:
    """Validate IP address format and characteristics."""
    result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "info": {
            "is_private": False,
            "is_localhost": False,
            "is_multicast": False,
            "version": None
        }
    }
    
    try:
        import ipaddress
        
        ip = ipaddress.ip_address(ip_address)
        result["info"]["version"] = ip.version
        
        # Check for private addresses
        if ip.is_private:
            result["info"]["is_private"] = True
            result["warnings"].append("Request from private IP address")
        
        # Check for localhost
        if ip.is_loopback:
            result["info"]["is_localhost"] = True
            result["warnings"].append("Request from localhost")
        
        # Check for multicast
        if ip.is_multicast:
            result["info"]["is_multicast"] = True
            result["warnings"].append("Request from multicast address")
        
        # Check for reserved ranges
        if ip.is_reserved:
            result["warnings"].append("Request from reserved IP range")
        
    except ValueError:
        result["errors"].append(f"Invalid IP address format: {ip_address}")
        result["is_valid"] = False
    except Exception:
        result["errors"].append("Error validating IP address")
        result["is_valid"] = False
    
    return result


async def _validate_user_agent(user_agent: str) -> Dict[str, Any]:
    """Validate User-Agent string for suspicious patterns."""
    result = {
        "is_suspicious": False,
        "warnings": []
    }
    
    try:
        # Check for empty or very short user agent
        if not user_agent or len(user_agent) < 10:
            result["is_suspicious"] = True
            result["warnings"].append("Suspicious: very short or empty User-Agent")
        
        # Check for bot patterns
        bot_patterns = [
            "bot", "crawler", "spider", "scraper", "wget", "curl"
        ]
        
        if any(pattern in user_agent.lower() for pattern in bot_patterns):
            result["warnings"].append("Bot/crawler User-Agent detected")
        
        # Check for suspicious patterns
        suspicious_patterns = [
            "python-requests", "urllib", "libwww", "java/", "go-http-client"
        ]
        
        if any(pattern in user_agent.lower() for pattern in suspicious_patterns):
            result["is_suspicious"] = True
            result["warnings"].append("Suspicious: programmatic User-Agent")
        
        # Check for very long user agent
        if len(user_agent) > 500:
            result["is_suspicious"] = True
            result["warnings"].append("Suspicious: very long User-Agent")
        
    except Exception:
        result["warnings"].append("Error analyzing User-Agent")
    
    return result


async def _check_ip_geolocation(ip_address: str) -> Dict[str, Any]:
    """Check IP geolocation (mock implementation)."""
    result = {
        "country": "Unknown",
        "region": "Unknown",
        "city": "Unknown"
    }
    
    try:
        # Mock geolocation - would normally use GeoIP service
        # For demonstration, assign based on IP patterns
        if ip_address.startswith("192.168."):
            result["country"] = "Private"
        elif ip_address.startswith("10."):
            result["country"] = "Private"
        else:
            result["country"] = "US"  # Default for demo
        
    except Exception:
        pass
    
    return result


async def _detect_vpn_proxy(ip_address: str) -> Dict[str, Any]:
    """Detect VPN/proxy usage (mock implementation)."""
    result = {
        "is_vpn": False,
        "is_tor": False,
        "is_proxy": False
    }
    
    try:
        # Mock implementation - would normally use VPN detection service
        # For demo, consider certain IP patterns as VPN
        if any(pattern in ip_address for pattern in ["vpn", "proxy", "tor"]):
            result["is_vpn"] = True
        
    except Exception:
        pass
    
    return result


async def _sanitize_single_input(
    input_name: str,
    input_value: Any,
    sanitization_rules: Dict[str, Any]
) -> Dict[str, Any]:
    """Sanitize a single input value."""
    result = {
        "sanitized_value": input_value,
        "was_sanitized": False,
        "violations": [],
        "warnings": [],
        "threats": []
    }
    
    try:
        if not isinstance(input_value, str):
            return result
        
        original_value = input_value
        sanitized_value = input_value
        
        # Check for SQL injection
        if sanitization_rules.get("check_sql_injection", True):
            sql_patterns = [
                r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)',
                r'(\bDROP\b|\bCREATE\b|\bALTER\b)',
                r'(\'|"|;|--|\*|\/\*|\*\/)'
            ]
            
            for pattern in sql_patterns:
                if re.search(pattern, sanitized_value, re.IGNORECASE):
                    result["violations"].append("SQL injection pattern detected")
                    result["threats"].append("sql_injection")
                    # Remove the pattern
                    sanitized_value = re.sub(pattern, '', sanitized_value, flags=re.IGNORECASE)
                    result["was_sanitized"] = True
        
        # Check for XSS
        if sanitization_rules.get("check_xss", True):
            xss_patterns = [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'on\w+\s*=',
                r'<iframe[^>]*>.*?</iframe>'
            ]
            
            for pattern in xss_patterns:
                if re.search(pattern, sanitized_value, re.IGNORECASE):
                    result["violations"].append("XSS pattern detected")
                    result["threats"].append("xss")
                    # Remove the pattern
                    sanitized_value = re.sub(pattern, '', sanitized_value, flags=re.IGNORECASE)
                    result["was_sanitized"] = True
        
        # Check for command injection
        if sanitization_rules.get("check_command_injection", True):
            command_patterns = [
                r'(\||&|;|\$\(|\`)',
                r'(\.\./|\.\.\\)',
                r'(\bcat\b|\bls\b|\brm\b|\bmv\b|\bcp\b)'
            ]
            
            for pattern in command_patterns:
                if re.search(pattern, sanitized_value):
                    result["violations"].append("Command injection pattern detected")
                    result["threats"].append("command_injection")
                    # Remove the pattern
                    sanitized_value = re.sub(pattern, '', sanitized_value)
                    result["was_sanitized"] = True
        
        # Strip HTML if requested
        if sanitization_rules.get("strip_html", True):
            html_pattern = r'<[^>]+>'
            if re.search(html_pattern, sanitized_value):
                sanitized_value = re.sub(html_pattern, '', sanitized_value)
                result["was_sanitized"] = True
                result["warnings"].append("HTML tags stripped")
        
        # Check length limits
        max_length = sanitization_rules.get("max_input_length", 10000)
        if len(sanitized_value) > max_length:
            sanitized_value = sanitized_value[:max_length]
            result["was_sanitized"] = True
            result["warnings"].append(f"Input truncated to {max_length} characters")
        
        result["sanitized_value"] = sanitized_value
        
    except Exception:
        result["warnings"].append("Error during input sanitization")
    
    return result


async def _analyze_threat_patterns(threats: List[str]) -> Dict[str, Any]:
    """Analyze threat patterns for coordinated attacks."""
    result = {
        "is_coordinated_attack": False,
        "warnings": []
    }
    
    try:
        # Count threat types
        threat_counts = {}
        for threat in threats:
            threat_counts[threat] = threat_counts.get(threat, 0) + 1
        
        # Check for multiple threat types (potential coordinated attack)
        if len(threat_counts) >= 3:
            result["is_coordinated_attack"] = True
            result["warnings"].append("Multiple attack vectors detected")
        
        # Check for high frequency of same threat
        for threat_type, count in threat_counts.items():
            if count >= 5:
                result["warnings"].append(f"High frequency {threat_type} attempts: {count}")
        
    except Exception:
        result["warnings"].append("Error analyzing threat patterns")
    
    return result