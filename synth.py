import soundfile as sf


class Synth:
    def __init__(self, name):
        self.name = name

    def play(self, note):
        print(f"{self.name} is playing {note}")
    
    def write(self, output_filename):
        """
        write() saves the modified audio array to a new .wav file at the original sample rate.
        """
        # Write audio data using soundfile module
        sf.write(output_filename, self.audio_data, self.samplerate)


    def parseMelody(self, melody):
        """
        parseMelody() takes a string of MIDI note numbers separated by commas and the bpm and then synthesises the melody
        """
        # Split the melody string into individual MIDI note numbers
        midi_notes = melody.split(',')
        # plays the melody 
        frequencies = []
        for note in midi_notes:
            note = note.strip()  # Remove any leading/trailing whitespace
            if note.isdigit():  # Check if the note is a valid MIDI number
                midi_number = int(note)
                frequency = self.midi_to_freq(midi_number)
                frequencies.append(frequency)
                print(f"Playing MIDI note {midi_number} at frequency {frequency:.2f} Hz")
            else:
                print(f"Invalid MIDI note: {note}")


# usage
synth = Synth("My Synth")
synth.play("audioeffects/audio1.wav")

path = input("Enter the path to the melody file: ")
with open(path, 'r') as file:
    melody = file.read()
frequencies = synth.parseMelody(melody)
print("Frequencies for the melody:", frequencies)  
