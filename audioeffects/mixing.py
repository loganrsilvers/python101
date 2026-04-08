'''
Import two different sound files of the same length. Mix down the two sounds to a single array. Play the resulting waveform using the sounddevice module.
'''

#Import two different sound files of the same length. 
# Mix down the two sounds to a single array. 
# Play the resulting waveform using the sounddevice module.
import soundfile as sf
import sounddevice as sd

def mix_down(audio_file1, audio_file2):
    data1, samplerate1 = sf.read(audio_file1)
    data2, samplerate2 = sf.read(audio_file2)

    if samplerate1 != samplerate2:
        raise ValueError("Sample rates of the two audio files must be the same.")

    if data1.shape[0] != data2.shape[0]:
        raise ValueError("Audio files must have the same number of samples.")

    # Mix down the two sounds to a single array
    mixed_data = (data1 + data2) / 2

    return mixed_data, samplerate1
# Play the resulting waveform using the sounddevice module.
mixed_audio, samplerate = mix_down('audio1.wav', 'audio2.wav')

# Export the resulting waveform as a WAV file
sf.write('mixed_output.wav', mixed_audio, samplerate)
