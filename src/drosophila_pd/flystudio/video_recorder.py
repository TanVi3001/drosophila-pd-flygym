from abc import ABC, abstractmethod

class VideoRecorder(ABC):
    """Abstract interface for video recording."""

    @abstractmethod
    def start_recording(self, file_path: str, format: str = "mp4", fps: int = 30) -> None:
        """Start recording. Supported formats: png sequence, gif, mp4, webm."""
        pass

    @abstractmethod
    def add_frame(self, frame_data: bytes) -> None:
        """Add a frame to the recording."""
        pass

    @abstractmethod
    def stop_recording(self) -> None:
        """Stop recording and finalize the file."""
        pass
