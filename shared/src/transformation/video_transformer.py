"""
Video transformer using FFmpeg
Applies color grading, flips, and basic filters to videos
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

import ffmpeg

from shared.src.transformation.exceptions import TransformationError

logger = logging.getLogger(__name__)


class VideoTransformer:
    """Video transformer using FFmpeg"""

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize video transformer
        
        Args:
            output_dir: Directory to save transformed videos (default: temp directory)
        """
        self.output_dir = output_dir or tempfile.gettempdir()
        os.makedirs(self.output_dir, exist_ok=True)

    def _build_color_grading_filter(self, params: Dict[str, float]) -> str:
        """
        Build FFmpeg color grading filter
        
        Args:
            params: Dictionary with brightness, contrast, saturation, hue values
            
        Returns:
            FFmpeg filter string
        """
        brightness = params.get("brightness", 0.0)
        contrast = params.get("contrast", 1.0)
        saturation = params.get("saturation", 1.0)
        hue = params.get("hue", 0.0)
        
        # FFmpeg eq filter: brightness (-1.0 to 1.0), contrast (0.0 to 3.0), saturation (0.0 to 3.0), hue (-180.0 to 180.0)
        # Convert hue from -180/180 to -1/1 range for eq filter
        hue_normalized = hue / 180.0
        
        return f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}:hue={hue_normalized}"

    def _build_flip_filter(self, params: Dict[str, bool]) -> List[str]:
        """
        Build FFmpeg flip filters
        
        Args:
            params: Dictionary with horizontal and vertical flip flags
            
        Returns:
            List of FFmpeg filter strings
        """
        filters = []
        if params.get("horizontal", False):
            filters.append("hflip")
        if params.get("vertical", False):
            filters.append("vflip")
        return filters

    def _build_blur_filter(self, radius: float) -> Optional[str]:
        """
        Build FFmpeg blur filter
        
        Args:
            radius: Blur radius (0.0 = no blur, higher = more blur)
            
        Returns:
            FFmpeg filter string or None if no blur
        """
        if radius <= 0.0:
            return None
        # boxblur filter: radius:radius (luma and chroma)
        return f"boxblur={radius}:{radius}"

    def _build_sharpen_filter(self, strength: float) -> Optional[str]:
        """
        Build FFmpeg sharpen filter
        
        Args:
            strength: Sharpen strength (0.0 = no sharpen, higher = more sharpen)
            
        Returns:
            FFmpeg filter string or None if no sharpen
        """
        if strength <= 0.0:
            return None
        # unsharp filter: luma_msize_x:luma_msize_y:luma_amount:chroma_msize_x:chroma_msize_y:chroma_amount
        # Using moderate values with strength multiplier
        luma_amount = 1.0 * strength
        return f"unsharp=5:5:{luma_amount}:5:5:0.0"

    def _build_noise_reduction_filter(self, strength: float) -> Optional[str]:
        """
        Build FFmpeg noise reduction filter
        
        Args:
            strength: Noise reduction strength (0.0 = no reduction, higher = more reduction)
            
        Returns:
            FFmpeg filter string or None if no reduction
        """
        if strength <= 0.0:
            return None
        # hqdn3d filter: luma_spatial:chroma_spatial:luma_temporal:chroma_temporal
        # Scale strength to reasonable values (2-8 range)
        luma_spatial = 2.0 + (strength * 6.0)
        chroma_spatial = 1.5 + (strength * 4.5)
        luma_temporal = 3.0 + (strength * 3.0)
        chroma_temporal = 2.25 + (strength * 2.25)
        return f"hqdn3d={luma_spatial}:{chroma_spatial}:{luma_temporal}:{chroma_temporal}"

    def _build_filter_complex(self, params: Dict[str, Any]) -> str:
        """
        Build complete FFmpeg filter complex from parameters
        
        Args:
            params: Transformation parameters dictionary
            
        Returns:
            FFmpeg filter complex string
        """
        filters = []
        
        # Color grading
        if "color_grading" in params:
            color_filter = self._build_color_grading_filter(params["color_grading"])
            filters.append(color_filter)
        
        # Flip effects
        if "flip" in params:
            flip_filters = self._build_flip_filter(params["flip"])
            filters.extend(flip_filters)
        
        # Blur
        if "filters" in params and "blur" in params["filters"]:
            blur_filter = self._build_blur_filter(params["filters"]["blur"])
            if blur_filter:
                filters.append(blur_filter)
        
        # Sharpen
        if "filters" in params and "sharpen" in params["filters"]:
            sharpen_filter = self._build_sharpen_filter(params["filters"]["sharpen"])
            if sharpen_filter:
                filters.append(sharpen_filter)
        
        # Noise reduction
        if "filters" in params and "noise_reduction" in params["filters"]:
            noise_filter = self._build_noise_reduction_filter(params["filters"]["noise_reduction"])
            if noise_filter:
                filters.append(noise_filter)
        
        # Combine filters with comma
        if filters:
            return ",".join(filters)
        return None

    def transform(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Transform video with specified parameters
        
        Args:
            input_file: Path to input video file
            output_file: Path to output video file (auto-generated if not provided)
            params: Transformation parameters dictionary
            
        Returns:
            Dictionary with transformation information:
            - output_file: Path to transformed file
            - file_size: File size in bytes
            - processing_time: Processing time in seconds (if tracked)
            
        Raises:
            TransformationError: If transformation fails
        """
        if not os.path.exists(input_file):
            raise TransformationError(f"Input file not found: {input_file}")
        
        params = params or {}
        
        # Generate output filename if not provided
        if not output_file:
            input_path = Path(input_file)
            output_file = os.path.join(
                self.output_dir,
                f"{input_path.stem}_transformed{input_path.suffix}",
            )
        
        try:
            # Create FFmpeg input
            input_stream = ffmpeg.input(input_file)
            video_stream = input_stream.video
            audio_stream = input_stream.audio
            
            # Apply filters sequentially
            # Color grading
            if "color_grading" in params:
                color_params = params["color_grading"]
                brightness = color_params.get("brightness", 0.0)
                contrast = color_params.get("contrast", 1.0)
                saturation = color_params.get("saturation", 1.0)
                hue = color_params.get("hue", 0.0) / 180.0  # Normalize hue
                video_stream = video_stream.filter(
                    "eq",
                    brightness=brightness,
                    contrast=contrast,
                    saturation=saturation,
                    hue=hue,
                )
            
            # Flip effects
            if "flip" in params:
                flip_params = params["flip"]
                if flip_params.get("horizontal", False):
                    video_stream = video_stream.hflip()
                if flip_params.get("vertical", False):
                    video_stream = video_stream.vflip()
            
            # Basic filters
            if "filters" in params:
                filter_params = params["filters"]
                
                # Blur
                if filter_params.get("blur", 0.0) > 0.0:
                    radius = filter_params["blur"]
                    video_stream = video_stream.filter("boxblur", radius, radius)
                
                # Sharpen
                if filter_params.get("sharpen", 0.0) > 0.0:
                    strength = filter_params["sharpen"]
                    luma_amount = 1.0 * strength
                    video_stream = video_stream.filter("unsharp", 5, 5, luma_amount, 5, 5, 0.0)
                
                # Noise reduction
                if filter_params.get("noise_reduction", 0.0) > 0.0:
                    strength = filter_params["noise_reduction"]
                    luma_spatial = 2.0 + (strength * 6.0)
                    chroma_spatial = 1.5 + (strength * 4.5)
                    luma_temporal = 3.0 + (strength * 3.0)
                    chroma_temporal = 2.25 + (strength * 2.25)
                    video_stream = video_stream.filter("hqdn3d", luma_spatial, chroma_spatial, luma_temporal, chroma_temporal)
            
            # Frame rate adjustment
            if "frame_rate" in params:
                frame_rate_params = params["frame_rate"]
                target_fps = frame_rate_params.get("target_fps")
                if target_fps and target_fps > 0:
                    # Use fps filter to change frame rate
                    video_stream = video_stream.filter("fps", fps=target_fps)
            
            # Aspect ratio modifications
            if "aspect_ratio" in params:
                aspect_params = params["aspect_ratio"]
                action = aspect_params.get("action")
                target_ratio = aspect_params.get("target_ratio")
                
                if action and target_ratio:
                    # Parse target ratio (e.g., "16:9" -> 16/9)
                    try:
                        ratio_parts = target_ratio.split(":")
                        target_ratio_value = float(ratio_parts[0]) / float(ratio_parts[1])
                    except (ValueError, IndexError):
                        logger.warning(f"Invalid target ratio: {target_ratio}, skipping aspect ratio modification")
                    else:
                        # Note: For proper crop/pad, we need video dimensions
                        # This is a simplified version - in production, probe video first
                        if action == "crop":
                            # Crop to target aspect ratio (maintains width, adjusts height)
                            # Simplified: crop to maintain width and adjust height
                            video_stream = video_stream.filter("crop", "iw", f"iw/{target_ratio_value}", "0", "0")
                        elif action == "pad":
                            # Pad to target aspect ratio
                            pad_color = aspect_params.get("color", "black")
                            # Pad to maintain height and adjust width
                            video_stream = video_stream.filter("pad", f"ih*{target_ratio_value}", "ih", "(ow-iw)/2", "0", color=pad_color)
            
            # Output settings for high quality
            output_stream = ffmpeg.output(
                video_stream,
                audio_stream,
                output_file,
                vcodec="libx264",
                preset="medium",  # Balance between speed and quality
                crf=20,  # High quality (18-23 range, lower = better quality)
                acodec="copy",  # Copy audio without re-encoding
            )
            
            # Run FFmpeg
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            # Get output file size
            file_size = os.path.getsize(output_file)
            
            return {
                "output_file": output_file,
                "file_size": file_size,
                "params": params,
            }
            
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise TransformationError(f"FFmpeg error: {error_message}") from e
        except Exception as e:
            raise TransformationError(f"Unexpected error transforming video: {str(e)}") from e

    def replace_audio(
        self,
        input_file: str,
        audio_file: str,
        output_file: Optional[str] = None,
        normalize: bool = True,
        match_volume: bool = False,
        audio_bitrate: Optional[str] = None,
        audio_sample_rate: Optional[int] = None,
        loop_audio: bool = True,
    ) -> Dict[str, Any]:
        """
        Replace audio track in video with new audio file
        
        Args:
            input_file: Path to input video file
            audio_file: Path to audio file to use as replacement
            output_file: Path to output video file (auto-generated if not provided)
            normalize: Normalize audio levels (default: True)
            match_volume: Match volume to original audio (default: False)
            audio_bitrate: Audio bitrate (e.g., "192k", "256k") (default: auto)
            audio_sample_rate: Audio sample rate in Hz (e.g., 44100, 48000) (default: auto)
            loop_audio: Loop audio if shorter than video (default: True)
            
        Returns:
            Dictionary with replacement information:
            - output_file: Path to output file
            - file_size: File size in bytes
            - audio_duration: Duration of audio file
            - video_duration: Duration of video file
            
        Raises:
            TransformationError: If replacement fails
        """
        if not os.path.exists(input_file):
            raise TransformationError(f"Input video file not found: {input_file}")
        if not os.path.exists(audio_file):
            raise TransformationError(f"Audio file not found: {audio_file}")
        
        # Generate output filename if not provided
        if not output_file:
            input_path = Path(input_file)
            output_file = os.path.join(
                self.output_dir,
                f"{input_path.stem}_audio_replaced{input_path.suffix}",
            )
        
        try:
            # Probe video to get duration
            video_probe = ffmpeg.probe(input_file)
            video_duration = float(video_probe['format']['duration'])
            
            # Probe audio to get duration
            audio_probe = ffmpeg.probe(audio_file)
            audio_duration = float(audio_probe['format']['duration'])
            
            # Create inputs
            video_input = ffmpeg.input(input_file)
            audio_input = ffmpeg.input(audio_file)
            
            # Process audio
            audio_stream = audio_input.audio
            
            # Normalize audio if requested
            if normalize:
                # Use loudnorm filter for normalization
                audio_stream = audio_stream.filter("loudnorm", I=-16.0, TP=-1.5, LRA=11.0)
            
            # Match volume to original if requested
            if match_volume:
                # Get original audio volume
                try:
                    original_audio = video_input.audio
                    # Use volume filter to match (simplified - would need analysis in production)
                    # For MVP, we'll skip this or use a simple approach
                    pass
                except:
                    # Video might not have audio, skip matching
                    pass
            
            # Loop audio if shorter than video and loop_audio is True
            if audio_duration < video_duration and loop_audio:
                # Use aloop filter to loop audio
                # Calculate number of loops needed (with some buffer)
                loops_needed = int((video_duration / audio_duration) + 1)
                # Use aloop filter - loop parameter is the number of loops, size is max samples (2e+09 = 2 billion samples)
                # Note: aloop syntax: aloop=loop:size
                audio_stream = audio_stream.filter("aloop", loop=loops_needed, size=2e+09)
            
            # Trim audio to match video duration if longer
            if audio_duration > video_duration:
                audio_stream = audio_stream.filter("atrim", duration=video_duration)
            
            # Build audio codec options
            audio_codec_options = {}
            if audio_bitrate:
                audio_codec_options['b:a'] = audio_bitrate
            if audio_sample_rate:
                audio_codec_options['ar'] = audio_sample_rate
            
            # Use AAC codec for audio (widely supported)
            if not audio_codec_options:
                audio_codec_options = {'acodec': 'aac', 'b:a': '192k', 'ar': 44100}
            else:
                audio_codec_options['acodec'] = 'aac'
            
            # Output: copy video stream (no re-encoding), replace audio
            # Build output with video copy and new audio
            output_kwargs = {
                "vcodec": "copy",  # Copy video without re-encoding to preserve quality
            }
            output_kwargs.update(audio_codec_options)
            
            output_stream = ffmpeg.output(
                video_input.video,
                audio_stream,
                output_file,
                **output_kwargs,
            )
            
            # Run FFmpeg
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            # Get output file size
            file_size = os.path.getsize(output_file)
            
            return {
                "output_file": output_file,
                "file_size": file_size,
                "audio_duration": audio_duration,
                "video_duration": video_duration,
            }
            
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise TransformationError(f"FFmpeg error replacing audio: {error_message}") from e
        except Exception as e:
            raise TransformationError(f"Unexpected error replacing audio: {str(e)}") from e
