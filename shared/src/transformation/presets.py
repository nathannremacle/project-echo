"""
Default transformation presets
"""

from typing import Dict, Any


def get_default_presets() -> Dict[str, Dict[str, Any]]:
    """
    Get default transformation presets
    
    Returns:
        Dictionary of preset names to parameter dictionaries
    """
    return {
        "subtle": {
            "color_grading": {
                "brightness": 0.05,
                "contrast": 1.05,
                "saturation": 1.1,
                "hue": 0.0,
            },
            "flip": {
                "horizontal": False,
                "vertical": False,
            },
            "filters": {
                "blur": 0.0,
                "sharpen": 0.0,
                "noise_reduction": 0.0,
            },
        },
        "moderate": {
            "color_grading": {
                "brightness": 0.1,
                "contrast": 1.1,
                "saturation": 1.2,
                "hue": 5.0,
            },
            "flip": {
                "horizontal": True,
                "vertical": False,
            },
            "filters": {
                "blur": 0.0,
                "sharpen": 0.2,
                "noise_reduction": 0.1,
            },
        },
        "strong": {
            "color_grading": {
                "brightness": 0.15,
                "contrast": 1.15,
                "saturation": 1.3,
                "hue": 10.0,
            },
            "flip": {
                "horizontal": True,
                "vertical": False,
            },
            "filters": {
                "blur": 0.0,
                "sharpen": 0.3,
                "noise_reduction": 0.2,
            },
        },
        "color_only": {
            "color_grading": {
                "brightness": 0.1,
                "contrast": 1.1,
                "saturation": 1.2,
                "hue": 0.0,
            },
            "flip": {
                "horizontal": False,
                "vertical": False,
            },
            "filters": {
                "blur": 0.0,
                "sharpen": 0.0,
                "noise_reduction": 0.0,
            },
        },
        "flip_only": {
            "color_grading": {
                "brightness": 0.0,
                "contrast": 1.0,
                "saturation": 1.0,
                "hue": 0.0,
            },
            "flip": {
                "horizontal": True,
                "vertical": False,
            },
            "filters": {
                "blur": 0.0,
                "sharpen": 0.0,
                "noise_reduction": 0.0,
            },
        },
    }


def get_preset(name: str) -> Dict[str, Any]:
    """
    Get a specific preset by name
    
    Args:
        name: Preset name
        
    Returns:
        Preset parameters dictionary
        
    Raises:
        KeyError: If preset not found
    """
    presets = get_default_presets()
    if name not in presets:
        raise KeyError(f"Preset '{name}' not found. Available: {list(presets.keys())}")
    return presets[name]
