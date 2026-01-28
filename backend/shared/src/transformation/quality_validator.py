"""
Quality validation utilities for transformed videos
"""

import os
from typing import Dict, Any, Optional
import ffmpeg


class QualityValidator:
    """Validates video quality after transformation"""

    def __init__(self):
        """Initialize quality validator"""
        pass

    def validate_video(self, video_path: str) -> Dict[str, Any]:
        """
        Validate video quality and properties
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with validation results:
            - valid: bool
            - resolution: (width, height)
            - duration: float (seconds)
            - file_size: int (bytes)
            - errors: List[str]
        """
        errors = []
        
        # Check file exists
        if not os.path.exists(video_path):
            return {
                "valid": False,
                "errors": [f"File not found: {video_path}"],
            }
        
        # Get file size
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            errors.append("File is empty")
        
        try:
            # Probe video with FFmpeg
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)
            
            if not video_stream:
                errors.append("No video stream found")
                return {
                    "valid": False,
                    "errors": errors,
                }
            
            # Extract properties
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            duration = float(probe.get("format", {}).get("duration", 0))
            
            # Basic validation checks
            if width == 0 or height == 0:
                errors.append("Invalid resolution")
            
            if duration == 0:
                errors.append("Invalid duration")
            
            # Check minimum resolution (720p)
            if height < 720:
                errors.append(f"Resolution too low: {height}p (minimum 720p)")
            
            return {
                "valid": len(errors) == 0,
                "resolution": (width, height),
                "duration": duration,
                "file_size": file_size,
                "errors": errors,
            }
            
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            errors.append(f"FFmpeg probe error: {error_message}")
            return {
                "valid": False,
                "errors": errors,
            }
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")
            return {
                "valid": False,
                "errors": errors,
            }

    def compare_quality(self, original_path: str, transformed_path: str) -> Dict[str, Any]:
        """
        Compare quality between original and transformed video
        
        Args:
            original_path: Path to original video
            transformed_path: Path to transformed video
            
        Returns:
            Dictionary with comparison results
        """
        original = self.validate_video(original_path)
        transformed = self.validate_video(transformed_path)
        
        comparison = {
            "original_valid": original.get("valid", False),
            "transformed_valid": transformed.get("valid", False),
            "resolution_preserved": False,
            "errors": [],
        }
        
        if original.get("valid") and transformed.get("valid"):
            orig_res = original.get("resolution")
            trans_res = transformed.get("resolution")
            
            if orig_res and trans_res:
                # Check if resolution is preserved (within tolerance)
                width_diff = abs(orig_res[0] - trans_res[0])
                height_diff = abs(orig_res[1] - trans_res[1])
                
                # Allow small differences due to encoding
                comparison["resolution_preserved"] = width_diff <= 2 and height_diff <= 2
                
                if not comparison["resolution_preserved"]:
                    comparison["errors"].append(
                        f"Resolution changed: {orig_res} -> {trans_res}"
                    )
        
        return comparison
