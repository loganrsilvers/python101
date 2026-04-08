import soundfile as sf
import sounddevice as sd
import numpy as np
from scipy.signal import convolve

class AudioEffects:

    def _load_audio(self, audio_file):
        """Helper method to load audio file"""
        return sf.read(audio_file)

    def _validate_compatible_files(self, data1, data2, samplerate1, samplerate2):
        """Helper method to validate two audio files are compatible"""
        if samplerate1 != samplerate2:
            raise ValueError("Sample rates must be the same.")
        if data1.shape[0] != data2.shape[0]:
            raise ValueError("Audio files must have the same number of samples.")

    def fade_in_out(self, audio_file):
        data, samplerate = self._load_audio(audio_file)
        fade_samples = int(samplerate * 5)

        fade_in_envelope = np.linspace(0, 1, fade_samples)
        fade_out_envelope = np.linspace(1, 0, fade_samples)

        data[:fade_samples] *= fade_in_envelope[:, np.newaxis]
        data[-fade_samples:] *= fade_out_envelope[:, np.newaxis]

        return data, samplerate

    def mix_down(self, audio_file1, audio_file2):
        data1, sr1 = self._load_audio(audio_file1)
        data2, sr2 = self._load_audio(audio_file2)
        self._validate_compatible_files(data1, data2, sr1, sr2)

        return (data1 + data2) / 2, sr1

    def mono_to_stereo(self, audio_file1, audio_file2):
        data1, sr1 = self._load_audio(audio_file1)
        data2, sr2 = self._load_audio(audio_file2)
        self._validate_compatible_files(data1, data2, sr1, sr2)

        if data1.ndim == 1 and data2.ndim == 1:
            stereo_data = np.column_stack((data1, data2))
        elif data1.ndim == 2 and data2.ndim == 2:
            stereo_data = np.column_stack((data1[:, 0], data2[:, 1]))
        else:
            raise ValueError("Both audio files must be either mono or stereo.")

        return stereo_data, sr1

    def apply_convolution_reverb(self, audio_file, impulse_response_file, output_file):
        audio_data, sr_audio = self._load_audio(audio_file)
        impulse_response, sr_ir = self._load_audio(impulse_response_file)

        if sr_audio != sr_ir:
            raise ValueError("Sample rates must be the same.")

        convolved_data = convolve(audio_data, impulse_response, mode='full')
        sf.write(output_file, convolved_data, sr_audio)
