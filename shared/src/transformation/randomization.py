"""
Parameter randomization utilities for video transformation
Ensures uniqueness by randomizing parameters within ranges
"""

import random
from typing import Dict, Any, Tuple, Optional


def randomize_params(base_params: Dict[str, Any], ranges: Dict[str, Tuple[float, float]]) -> Dict[str, Any]:
    """
    Randomize transformation parameters within specified ranges
    
    Args:
        base_params: Base parameters dictionary
        ranges: Dictionary mapping parameter paths to (min, max) tuples
                Example: {"color_grading.brightness": (-0.05, 0.05)}
        
    Returns:
        Randomized parameters dictionary
    """
    import copy
    
    randomized = copy.deepcopy(base_params)
    
    for param_path, (min_val, max_val) in ranges.items():
        # Navigate nested dictionary
        keys = param_path.split(".")
        current = randomized
        
        # Navigate to parent dict
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Get base value or default
        final_key = keys[-1]
        base_value = current.get(final_key, 0.0) if isinstance(current, dict) else 0.0
        
        # Randomize within range
        if isinstance(base_value, (int, float)):
            random_value = base_value + random.uniform(min_val, max_val)
            # Clamp to reasonable bounds
            if final_key == "brightness":
                random_value = max(-1.0, min(1.0, random_value))
            elif final_key == "contrast":
                random_value = max(0.0, min(3.0, random_value))
            elif final_key == "saturation":
                random_value = max(0.0, min(3.0, random_value))
            elif final_key == "hue":
                random_value = max(-180.0, min(180.0, random_value))
            
            if isinstance(current, dict):
                current[final_key] = random_value
    
    return randomized


def get_default_randomization_ranges() -> Dict[str, Tuple[float, float]]:
    """
    Get default randomization ranges for transformation parameters
    
    Returns:
        Dictionary of parameter paths to (min, max) ranges
    """
    return {
        "color_grading.brightness": (-0.05, 0.05),
        "color_grading.contrast": (-0.05, 0.05),
        "color_grading.saturation": (-0.1, 0.1),
        "color_grading.hue": (-5.0, 5.0),
        "filters.blur": (0.0, 0.5),
        "filters.sharpen": (0.0, 0.2),
        "filters.noise_reduction": (0.0, 0.1),
    }


def randomize_preset_params(preset_params: Dict[str, Any], randomization_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Randomize preset parameters based on configuration
    
    Args:
        preset_params: Preset parameters dictionary
        randomization_config: Randomization configuration
            {
                "enabled": True,
                "ranges": {...}  # Optional custom ranges
            }
        
    Returns:
        Randomized parameters dictionary (or original if disabled)
    """
    if not randomization_config or not randomization_config.get("enabled", False):
        return preset_params
    
    # Use custom ranges if provided, otherwise use defaults
    ranges = randomization_config.get("ranges") or get_default_randomization_ranges()
    
    return randomize_params(preset_params, ranges)
