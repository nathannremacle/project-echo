"""
Transformation-specific exceptions
"""


class TransformationError(Exception):
    """Base exception for transformation errors"""
    pass


class PresetNotFoundError(TransformationError):
    """Raised when transformation preset is not found"""
    pass


class InvalidParametersError(TransformationError):
    """Raised when transformation parameters are invalid"""
    pass
