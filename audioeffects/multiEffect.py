# 1. Import required modules

import soundfile as sf
import numpy as np


# 2. Class definition

class MultiEffect:
    """
    A class to apply various audio effects to multi-channel .wav files.
        filename (str): Path to the input audio file.
        audio_data (np.ndarray): NxC NumPy array containing audio samples.
        samplerate (int): Sample rate of the audio file in Hz.
        duration (float): Duration of the audio file in seconds.
        num_channels (int): Number of audio channels.
    """
    
    def __init__(self, filename):
        """
        Initialize the MultiEffect class by loading an audio file.
        """
        self.filename = filename
        
        # Read audio file using soundfile module
        self.audio_data, self.samplerate = sf.read(filename)
        
        # Ensure audio_data is 2D (handle mono files)
        if self.audio_data.ndim == 1:
            self.audio_data = self.audio_data.reshape(-1, 1)
        
        # Extract audio properties
        num_samples = self.audio_data.shape[0]
        self.duration = num_samples / self.samplerate
        self.num_channels = self.audio_data.shape[1]
    





    """
    reverse() - Flips the order of samples, so the sound plays backward.

    distort(clip_level)- Clips amplitudes above the threshold, simulating distortion.

    mirror() - Reverses channel order (e.g., Left ↔ Right for stereo).

    normalize(target_level) - Scales volume so the loudest sample reaches a target level without clipping.
    
    """



    def reverse(self):
        """
        Reverse all channels in time (play audio backwards).
        """
        # Flip audio data along the time axis (axis 0)
        self.audio_data = np.flip(self.audio_data, axis=0)
    
    def distort(self, clip_level):
        """
        This effect clips audio samples that exceed the specified threshold,
        creating a distorted sound characteristic of overdriven amplifiers.
        """
        # Clip audio data to the specified range
        self.audio_data = np.clip(self.audio_data, -clip_level, clip_level)
    
    def mirror(self):
        """
        - Stereo (2 channels): L/R becomes R/L
        - Multi-channel: Channels are reversed in order
        - Mono (1 channel): No effect
        """
        # Reverse column order (channels) along axis 1
        self.audio_data = np.fliplr(self.audio_data)
    
    def normalize(self, target_level=0.95):
        """
        custom audio effect that scales the entire audio
        signal so that the loudest peak reaches the specified target level.
        """
        # Find the maximum absolute value across all samples and channels
        max_level = np.max(np.abs(self.audio_data))
        
        # Avoid division by zero
        if max_level > 0:
            # Scale audio to reach the target level
            self.audio_data = self.audio_data * (target_level / max_level)
    
    def write(self, output_filename):
        """
        write() saves the modified audio array to a new .wav file at the original sample rate.
        """
        # Write audio data using soundfile module
        sf.write(output_filename, self.audio_data, self.samplerate)
    
    def __str__(self):
        """
        Return a string representation of the MultiEffect instance.
        """
        return (
            f"MultiEffect Audio Processor\n"
            f"{'='*40}\n"
            f"Input File: {self.filename}\n"
            f"Sample Rate: {self.samplerate} Hz\n"
            f"Duration: {self.duration:.2f} seconds\n"
            f"Channels: {self.num_channels}\n"
            f"Samples: {self.audio_data.shape[0]}\n"
            f"{'='*40}"
        )


# File paths for test audio (from the assignment zip)
monoWav = 'soundeffects-wav/mono.wav'
octoWav = 'soundeffects-wav/octo.wav'
stereoWav = 'soundeffects-wav/stereo.wav'


# ============================================================================
# DEMONSTRATION CODE
# ============================================================================

if __name__ == "__main__":
    """
    Demo code showcasing all features of the MultiEffect class.
    Uses the provided test files: mono.wav, stereo.wav, octo.wav
    """
    print("MultiEffect Audio Processing Demo\n")

    # Test mono audio
    print("=== Testing mono.wav ===")
    mono_effect = MultiEffect(monoWav)
    print(mono_effect)

    mono_effect.reverse()
    mono_effect.distort(0.5)
    mono_effect.normalize(0.9)
    mono_effect.write('mono_processed.wav')
    print("✓ mono_processed.wav written\n")

    # Test stereo audio
    print("=== Testing stereo.wav ===")
    stereo_effect = MultiEffect(stereoWav)
    print(stereo_effect)

    stereo_effect.mirror()
    stereo_effect.normalize(0.95)
    stereo_effect.write('stereo_processed.wav')
    print("✓ stereo_processed.wav written\n")

    # Test octo-channel audio
    print("=== Testing octo.wav ===")
    octo_effect = MultiEffect(octoWav)
    print(octo_effect)

    octo_effect.reverse()
    octo_effect.mirror()
    octo_effect.normalize(0.8)
    octo_effect.write('octo_processed.wav')
    print("✓ octo_processed.wav written\n")

    print("All effects applied and output files written successfully.")