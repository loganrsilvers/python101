'''
Import a sound file and apply a 1 second fade in and a 1.5 second fade out. Play the resulting waveform using the sounddevice module.
Import two different sound files of the same length. Mix down the two sounds to a single array. Play the resulting waveform using the sounddevice module.
Import two different sound files of the same length. If they are mono, use one as the left channel and the other as the right channel to create a new stereo sound. If the files are stereo, use the left channel of one file and the right channel of the other. Play the resulting waveform using the sounddevice module.
Import a sound file and this impulse response  Download this impulse response(download it from the Files page if you cannot download from this link). Apply convolution reverb using the given impule response. Export the resulting waveform as a WAV file.
'''

#Import a sound file and 
import soundfile as sf
import sounddevice as sd
import numpy as np


def fade_in_out(audio_file):
    data, samplerate = sf.read(audio_file)
    num_samples = data.shape[0]
    # apply a 5 second fade in 
    fade_in_samples = int(samplerate * 5)
    # and a 5 second fade out. 
    fade_out_samples = int(samplerate * 5) 

    # Create fade in and fade out envelopes
    fade_in_envelope = np.linspace(0, 1, fade_in_samples)
    fade_out_envelope = np.linspace(1, 0, fade_out_samples)

    # Apply fade in
    data[:fade_in_samples] *= fade_in_envelope[:, np.newaxis]

    # Apply fade out
    data[-fade_out_samples:] *= fade_out_envelope[:, np.newaxis]

    return data, samplerate
# export the resulting waveform 
# using the sounddevice module.
audio_data, samplerate = fade_in_out('audio1.wav')
sf.write('faded_output.wav', audio_data, samplerate)
