'''Import two different sound files of the same length. If they are mono, use one as the left channel and the other as the right channel to create a new stereo sound. If the files are stereo, use the left channel of one file and the right channel of the other. Play the resulting waveform using the sounddevice module.
'''

#Import two different sound files of the same length. 
# If they are mono, use one as the left channel 
# and the other as the right channel 
# to create a new stereo sound. 
# If the files are stereo, 
# use the left channel of one file 
# and the right channel of the other. 
# Play the resulting waveform using the sounddevice module.

import soundfile as sf
import sounddevice as sd

def mono_to_stereo(audio_file1, audio_file2):
    data1, samplerate1 = sf.read(audio_file1)
    data2, samplerate2 = sf.read(audio_file2)

    if samplerate1 != samplerate2:
        raise ValueError("Sample rates of the two audio files must be the same.")

    if data1.shape[0] != data2.shape[0]:
        raise ValueError("Audio files must have the same number of samples.")

    # Check if the files are mono or stereo
    if data1.ndim == 1 and data2.ndim == 1:
        # Both files are mono, create a new stereo sound
        stereo_data = np.column_stack((data1, data2))
    elif data1.ndim == 2 and data2.ndim == 2:
        # Both files are stereo, use left channel of one and right channel of the other
        stereo_data = np.column_stack((data1[:, 0], data2[:, 1]))
    else:
        raise ValueError("Both audio files must be either mono or stereo.")

    return stereo_data, samplerate1
# Play the resulting waveform using the sounddevice module.
stereo_audio, samplerate = mono_to_stereo('audio1.wav', 'audio2.wav')
sd.play(stereo_audio, samplerate)
