def midi_to_freq(num):
    # MIDI note 69 is A4, which is 440 Hz
    return 440 * (2 ** ((num - 69) / 12))  

#takes input from user
midi_numbers = []
while True:
    midi_input = input("Enter MIDI number (or 'done' to finish): ")
    if midi_input.lower() == "done":
        break
    midi_num = int(midi_input)
    midi_numbers.append(midi_num)

print("Frequencies:")
for num in midi_numbers:
    print(midi_to_freq(num))
