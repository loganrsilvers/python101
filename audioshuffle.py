import soundfile as sf
import numpy as np
import random as rand
import os

#Write an audio shuffler that takes an audio file 
# with variable number of channels 
# and shuffles its samples in the following way:
#repeats the process a number of times defined by the user
global final_audio_file
def audio_shuffle(audio_file, num_repeats):
    data, samplerate = sf.read(audio_file)
    num_samples = data.shape[0]
    for i in range(num_repeats):
        #splits the audio into three sections—ABC—randomly
        split1 = rand.randint(0, num_samples)
        split2 = rand.randint(split1, num_samples)
        a = data[:split1]
        b = data[split1:split2]
        c = data[split2:]

        #rearranges the sections into either 
        # BAC or ACB randomly
        if rand.random() < 0.5:
            new_data = np.concatenate((b, a, c))
        else:
            new_data = np.concatenate((a, c, b))

        #writes the audio to a new file
        final_audio_file = f'shuffled_{i}.wav'
        sf.write(final_audio_file, new_data, samplerate)

print(f"WE ARE HERE: {os.getcwd()} !!!!!!!!!!")
open('stereo.wav').close()
audio_shuffle('stereo.wav', 5)

