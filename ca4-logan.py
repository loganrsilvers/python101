import numpy as np
import sounddevice as sd
import soundfile as sf


class Synthesizer:
    '''
    monophonic additive synth 
    allows its user to specify a melody 
    to be synthesized 
    and optionally played 
    and/or saved to a .wav file.
    '''

    #First, the user should be prompted to input a melody as 
    # a comma-separated list of MIDI note numbers

    def getMIDInotes() -> list:
        while True:
            userInput = input(
               "\nInput the melody as a comma-separated list of MIDI notes\n"
            " (numbers should be 0-127, any negative number will count as a 'rest'):\n  > "
            ).strip()
            if not userInput:
                print("No input detected. Please try again.")
                continue 

            #errors
            try:
                notes = list(map(int, userInput.split(",")))
            except ValueError:
                print("Could not parse input, please make sure every value is an INT:")
                continue
            if len(notes) == 0:
                print("The list is empty, please enter at least one MIDI note (number 0-127): ")
                continue 

            #validating non-error input
            validNotes = []
            for note in notes:
                if note < 0:
                    # negitive numbers will be rest notes, so i will add them to the list
                    validNotes.append(note)
                elif note > 127:
                    print(f"Just to let you know, {note} is bigger than 127, so it will be changed to 127. ")
                    validNotes.append(127)
                else:
                    validNotes.append(note)
                
            print(f"You have {len(validNotes)} notes and rests")
            return validNotes
        
    '''
    Next, the user should be prompted to input the melody's tempo 
    in BPM (beats per minutes) 
    as a single float. 
    To keep it simple, consider each note's duration as equivalent to a single beat.
    '''

    def getBPM() -> float:
        while True:
            userInput = input(
                f"\n Please input the BPM/tempo for the beat. (must be a decimal between 10.0 and 400.0)"
            ).strip()

            #errors
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
    def synthTheMelody(
        self,
        validNotes: list,
        bpm: float,
    ) -> np.ndarray:
        
        beat_sec = self.bpm2sec(bpm)
        n_samples = self.sec2samples(beat_sec)
        
        audioChunks = []
        for theNote in validNotes:
            chunk = self.note(theNote, beat_sec)
            audioChunks.append(chunk)
        
        singleNumpyArray = np.concatenate(audioChunks)

        #uhh .. normalizes it
        peak = np.max(np.abs(singleNumpyArray))
        if peak > 0.0:
            singleNumpyArray = 0.9 * singleNumpyArray / peak
        
        return singleNumpyArray

    '''
    Next, the user should be prompted 
    to input either yes or no 
    '''

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
    def shouldAudioBePlayed(audio : np.ndarray, sampleRate: int) -> None:
        if not getYesorNo("\n Do you want to play the melody? "):
            return
        
        #error checking sounddevice
        if sd is None:
            print(" sd (sounddevice) isnt on here // so it wont run.")
            return
        

        '''
        directly from the NumPy array 
        to the sound card. 
        '''
        print("AUDIO PLAYING . AUDIO SHOULD BE PLAYING .")
        try:
            #Use the sounddevice module for this purpose.
            sd.play(audio.astype(np.float32), samplerate=sampleRate)
            sd.wait()
            print("AUDIO FINISHED PLAYING NOW .")
        except Exception as exc:
            print(f"UHH . This failed for THIS REASON : {exc}")


    #specify whether the melody should now be written to a .wav file.
    def doYouWantToSave2WAV(audio: np.ndarray, sampleRate: int) -> None:
        if not getYesorNo("\n DO you want to save the melody to a .WAV file?? "):
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
            sf.write(userInput, audio.astype(np.float32), sampleRate, subtype="PCM_16")
            print("I DID IT!")
        except Exception as exc:
            print(f"UHH . This failed for THIS REASON : {exc}")
            


    


