'''py -m pip install --upgrade pip
py -m pip install scipy
Import a sound file and this impulse response  Download this impulse response(download it from the Files page if you cannot download from this link). Apply convolution reverb using the given impule response. Export the resulting waveform as a WAV file.
'''

#Import a sound file and this impulse response  (IR1_click_response_dampers_down.wav)
import soundfile as sf
from scipy.signal import convolve

def apply_convolution_reverb(audio_file, impulse_response_file, output_file):
    audio_data, samplerate_audio = sf.read(audio_file)
    impulse_response, samplerate_ir = sf.read(impulse_response_file)

    if samplerate_audio != samplerate_ir:
        raise ValueError("Sample rates of the audio file and impulse response must be the same.")

    # Apply convolution reverb using the given impulse response
    convolved_data = convolve(audio_data, impulse_response, mode='full')

    # Export the resulting waveform as a WAV file
    sf.write(output_file, convolved_data, samplerate_audio)
# Apply convolution reverb using the given impule response. 
# Export the resulting waveform as a WAV file.
apply_convolution_reverb('audio1.wav', 'audio2.wav', 'convolved_output.wav')
