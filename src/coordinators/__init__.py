"""Service Coordinators for OpenRouter Anthropic Server.

High-level service coordinators that orchestrate complex workflows by
coordinating multiple tasks, flows, and services across the system.

Part of Phase 6C comprehensive refactoring - Service Coordinator Layer.
"""

from .tool_coordinator import tool_coordinator, ToolCoordinator
from .execution_coordinator import execution_coordinator, ExecutionCoordinator

# Service coordinator registry for easy access
COORDINATORS = {
    "tool": tool_coordinator,
    "execution": execution_coordinator
}

__all__ = [
    # Coordinator classes
    "ToolCoordinator",
    "ExecutionCoordinator",
    
    # Coordinator instances
    "tool_coordinator",
    "execution_coordinator",
    
    # Registry
    "COORDINATORS"
]


def get_coordinator(coordinator_type: str):
    """
    Get a coordinator instance by type.
    
    Args:
        coordinator_type: Type of coordinator ("tool", "execution")
    
    Returns:
        Coordinator instance
    
    Raises:
        ValueError: If coordinator type is not found
    """
    if coordinator_type not in COORDINATORS:
        available_types = list(COORDINATORS.keys())
        raise ValueError(f"Unknown coordinator type '{coordinator_type}'. Available types: {available_types}")
    
    return COORDINATORS[coordinator_type]


def get_all_coordinator_statistics():
    """
    Get statistics from all coordinators.
    
    Returns:
        Dict containing statistics from all coordinators
    """
    stats = {}
    
    for coord_type, coordinator in COORDINATORS.items():
        try:
            if hasattr(coordinator, 'get_statistics'):
                stats[coord_type] = coordinator.get_statistics()
            elif hasattr(coordinator, 'get_tool_statistics'):
                stats[coord_type] = coordinator.get_tool_statistics()
            elif hasattr(coordinator, 'get_validation_statistics'):
                stats[coord_type] = coordinator.get_validation_statistics()
            elif hasattr(coordinator, 'get_conversion_statistics'):
                stats[coord_type] = coordinator.get_conversion_statistics()
            else:
                stats[coord_type] = {"status": "no_statistics_method"}
        except Exception as e:
            stats[coord_type] = {"error": str(e)}
    
    return stats


async def run_all_health_checks():
    """
    Run health checks on all coordinators.
    
    Returns:
        Dict containing health check results from all coordinators
    """
    health_results = {}
    
    for coord_type, coordinator in COORDINATORS.items():
        try:
            if hasattr(coordinator, 'run_health_check'):
                result = await coordinator.run_health_check()
                health_results[coord_type] = result.converted_data if result.success else {"error": result.errors}
            elif hasattr(coordinator, 'run_tool_health_check'):
                result = await coordinator.run_tool_health_check()
                health_results[coord_type] = result.converted_data if result.success else {"error": result.errors}
            elif hasattr(coordinator, 'run_validation_health_check'):
                result = await coordinator.run_validation_health_check()
                health_results[coord_type] = result.converted_data if result.success else {"error": result.errors}
            elif hasattr(coordinator, 'run_conversion_health_check'):
                result = await coordinator.run_conversion_health_check()
                health_results[coord_type] = result.converted_data if result.success else {"error": result.errors}
            else:
                health_results[coord_type] = {"status": "no_health_check_method"}
        except Exception as e:
            health_results[coord_type] = {"error": str(e)}
    
    return health_results


def reset_all_coordinator_statistics():
    """
    Reset statistics on all coordinators.
    """
    for coord_type, coordinator in COORDINATORS.items():
        try:
            if hasattr(coordinator, 'reset_statistics'):
                coordinator.reset_statistics()
        except Exception as e:
            # Log error but continue with other coordinators
            pass


# Coordinator configuration management
DEFAULT_COORDINATOR_CONFIG = {
    "tool": {
        "max_concurrent_executions": 5,
        "execution_timeout": 30,
        "enable_health_monitoring": True,
        "enable_performance_tracking": True
    },
    "execution": {
        "enable_batch_processing": True,
        "batch_size": 10,
        "enable_metrics_collection": True,
        "workflow_timeout": 300
    }
}


def configure_all_coordinators(config: dict = None):
    """
    Configure all coordinators with provided configuration.
    
    Args:
        config: Configuration dict with coordinator-specific settings
    """
    if config is None:
        config = DEFAULT_COORDINATOR_CONFIG
    
    for coord_type, coordinator in COORDINATORS.items():
        coord_config = config.get(coord_type, {})
        
        try:
            if hasattr(coordinator, 'update_config'):
                coordinator.update_config(coord_config)
            elif hasattr(coordinator, 'update_tool_config'):
                coordinator.update_tool_config(coord_config)
            elif hasattr(coordinator, 'update_validation_config'):
                coordinator.update_validation_config(coord_config)
            elif hasattr(coordinator, 'update_conversion_config'):
                coordinator.update_conversion_config(coord_config)
        except Exception as e:
            # Log error but continue with other coordinators
            pass