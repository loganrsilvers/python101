import numpy as np
import sounddevice as sd
import soundfile as sf

# 60, 60, 60, 62, 64, 64, 62, 64, 65, 67, 72, 72, 72, 67, 67, 67, 64, 64, 64, 60, 60, 60, 67, 65, 64, 62, 60

class Synthesizer:
    '''
    monophonic additive synth 
    allows its user to specify a melody 
    to be synthesized 
    and optionally played 
    and/or saved to a .wav file.



    one part to handle input
    one part to generate the sound
    and separate parts to play/save the audio

    '''

    #initializer 
    def __init__(self, sampleRate=44100):
        self.sampleRate = sampleRate

    # First, the user should be prompted to input a melody as
    # a comma-separated list of MIDI note numbers
    @staticmethod
    def getMIDInotes() -> list:
        while True:
            userInput = input(
                "\nInput the melody as a comma-separated list of MIDI notes\n"
                " (numbers should be 0-127, any negative number will count as a 'rest'):\n  > "
            ).strip()
            if not userInput:
                print("No input detected. Please try again.")
                continue

            # errors
            try:
                notes = list(map(int, userInput.split(",")))
            except ValueError:
                print("Could not parse input, please make sure every value is an INT seperated by ONLY COMMAS NO SPACES:")
                continue
            if len(notes) == 0:
                print("The list is empty, please enter at least one MIDI note (number 0-127): ")
                continue

            # validating non-error input
            validNotes = []
            for note in notes:
                if note < 0:
                    # negitive numbers will be rest notes, so i will add them to the list
                    print(f"Note {note} is a rest.")
                    validNotes.append(note)
                elif note > 127:
                    print(f"Just to let you know, {note} is bigger than 127, so it will be changed to 127. ")
                    validNotes.append(127)
                else:
                    validNotes.append(note)

            print(f"You have {len(validNotes)} notes")
            return validNotes

    '''
    Next, the user should be prompted to input the melody's tempo
    in BPM (beats per minutes)
    as a single float.
    To keep it simple, consider each note's duration as equivalent to a single beat.
    '''
    @staticmethod
    def getBPM() -> float:
        while True:
            userInput = input(
                f"\n Please input the BPM/tempo for the beat. (must be a decimal between 10.0 and 400.0)"
            ).strip()

            # errors
            try:
                bpm = float(userInput)
            except ValueError:
                print("Please enter a decimal between 10.0 and 400.0")
                continue
            if bpm < 10.0:
                print(f"{bpm} is too slow. It will be bumped up to 10.0.")
                bpm = 10.0
            elif bpm > 400.0:
                print(f"{bpm} is wayyy too fast. It will be bumped down to 400.0.")
                bpm = 400.0

            print(f"The BPM/tempo is currently set to {bpm} BPM.")
            return bpm

    '''
    The script should then generate a single NumPy array
    that synthesizes this melody
    using some version of additive synthesis
    '''
    def note(self, midiNote: int, durationSec: float) -> np.ndarray:
        nSamples = self.sec2samples(durationSec)
        if midiNote < 0:
            return np.zeros(nSamples, dtype=np.float32)

        #evenly spaced numbers between 0 and durationSec, with nSamples total samples
        t = np.linspace(0, durationSec, nSamples, endpoint=False)
        freq = self.midi2freq(midiNote)

        # additive synthesis
        wave = (
            self.oscillator(freq, t)  # fundamental
        )
        # Apply the attack/decay envelope to shape the note's volume
        env = self.envelope(nSamples)
        return (wave * env).astype(np.float32)
    

    # this function will synthesize the entire melody 
    # by calling the note() function 
    # for each MIDI note in the list, 
    # concatenating the resulting audio chunks together, 
    # and normalizing the final audio to prevent clipping.
    def synthTheMelody(
        self,
        validNotes: list,
        bpm: float,
    ) -> np.ndarray:

        beat_sec = self.bpm2sec(bpm)

        audioChunks = []
        for theNote in validNotes:
            chunk = self.note(theNote, beat_sec)
            audioChunks.append(chunk)

        if len(audioChunks) == 0:
            return np.array([], dtype=np.float32)

        singleNumpyArray = np.concatenate(audioChunks)

        # uhh .. normalizes it at 0.9
        peak = np.max(np.abs(singleNumpyArray))
        if peak > 0.0:
            singleNumpyArray = 0.9 * singleNumpyArray / peak

        return singleNumpyArray

    '''
    Next, the user should be prompted
    to input either yes or no
    '''
    @staticmethod
    def getYesorNo(prompt: str) -> bool:
        while True:
            ans = input(prompt + "[yes/no]:").strip().lower()
            if ans in ("yes", "y"):
                return True
            if ans in ("no", "n"):
                return False
            print("Please enter a 'yes' or a 'no'.")

    '''
    to specify whether the melody should now be played
    '''
    def shouldAudioBePlayed(self, audio: np.ndarray) -> None:
        if not self.getYesorNo("\n Do you want to play the melody? "):
            return

        # error checking sounddevice
        if sd is None:
            print(" sd (sounddevice) isnt on here // so it wont run.")
            return

        '''
        directly from the NumPy array
        to the sound card.
        '''
        print("AUDIO PLAYING . AUDIO SHOULD BE PLAYING . PLEASE WAIT A SECOND OR TWO IF YOU PUT A LOW BPM . ")
        try:
            # Use the sounddevice module for this purpose.
            sd.play(audio.astype(np.float32), samplerate=self.sampleRate)
            sd.wait()
            print("AUDIO FINISHED PLAYING NOW .")
        except Exception as exc:
            print(f"UHH . This failed for THIS REASON : {exc}")

    # specify whether the melody should now be written to a .wav file.
    def doYouWantToSave2WAV(self, audio: np.ndarray) -> None:
        if not self.getYesorNo("\n DO you want to save the melody to a .WAV file?? "):
            return

        # Use the soundfile module from the pysoundfile package for this purpose
        if sf is None:
            print(" sf (soundfile) isnt on here // so it wont run.")
            return

        userInput = input(" pls enter a FILENAME for the WAV file (ex myWav for myWav.wav): \n > ").strip()
        if not userInput:
            userInput = "untitled.wav"
        if not userInput.lower().endswith(".wav"):
            userInput += ".wav"

        print(f"OKAY IM MAKING YOUR {userInput} FILE RIGHT NOW !!!")
        try:
            sf.write(userInput, audio.astype(np.float32), self.sampleRate, subtype="PCM_16")
            print("I DID IT!")
        except Exception as exc:
            print(f"UHH . This failed for THIS REASON : {exc}")

    
    '''
    Some ideas for functions that your script might define: midi2freq(), bpm2sec(), sec2samples(), oscillator(), envelope(), note(), melody().
    '''
    def bpm2sec(self, bpm: float) -> float:
        return 60.0 / bpm

    def sec2samples(self, seconds: float) -> int:
        return int(round(seconds * self.sampleRate))

    def midi2freq(self, midiNote: int) -> float: #Hz
        return 440.0 * (2.0 ** ((midiNote - 69) / 12.0))

    # sawtooth wave oscillator 
    # sums harmonics up to (sampleRate / 2)
    def oscillator(self, freq: float, t: np.ndarray) -> np.ndarray:
        """        
        sawtooth(t) = (1/n) * sin(2*pi*n*freq*t)
        to avoid distortion, only use is freq < (sampleRate / 2)
        """
        wave = np.zeros(len(t), dtype=np.float64)

        # add harmonics until we reach the min Nyquist frequency (sampleRate / 2)
        harmonic = 1
        while (harmonic * freq) < (self.sampleRate / 2.0):
            # amplitude decreases as 1/n (standard sawtooth partials)
            amplitude = 1.0 / harmonic
            # sawtooth(t) = (1/n) * sin(2*pi*n*freq*t)
            wave += amplitude * np.sin(2 * np.pi * harmonic * freq * t)
            harmonic += 1

        return wave.astype(np.float32)

    #envelope function that applies an attack-decay envelope to the note
    def envelope(self, nSamples: int, attackRatio=0.1, decayRatio=0.15) -> np.ndarray:
        """
        attack-decay amplitude envelope for 1 note.
        - Attack: 0 to 1 
          (attackRatio * nSamples).
        - Sustain: stay at 1
        - Decay: 1 to 0
          (decayRatio * nSamples)
        """
        env = np.ones(nSamples, dtype=np.float32)

        # number of samples for attack and decay phases
        attackSamples = int(nSamples * attackRatio)
        decaySamples = int(nSamples * decayRatio)

        # linear ramp up during the attack phase
        # attackSamples is the number of samples in the attack phase 
        # so we create a linear ramp from 0 to 1 over that many samples
        if attackSamples > 0:
            env[:attackSamples] = np.linspace(0.0, 1.0, attackSamples)

        # linear ramp down during the decay phase
        # decaySamples is the number of samples in the decay phase
        # so we create a linear ramp from 1 to 0 over that many samples 
        # (( at the end of the envelope
        if decaySamples > 0:
            env[nSamples - decaySamples:] = np.linspace(1.0, 0.0, decaySamples)

        return env


# use the class
synth = Synthesizer()

validNotes = synth.getMIDInotes()
bpm = synth.getBPM()
print("\nSynthesizing melody...")
audio = synth.synthTheMelody(validNotes, bpm)
print("Synthesis complete.")

synth.shouldAudioBePlayed(audio)

synth.doYouWantToSave2WAV(audio)