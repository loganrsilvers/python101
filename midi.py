def midi_to_freq(num):
    # MIDI note 69 is A4, which is 440 Hz
    return 440 * (2 ** ((num - 69) / 12))  

#takes input from user
numbers = []
while True:
    myinput = input("Enter MIDI number (or 'done' to finish): ")
    if myinput == "done":
        break
    else:
        item = int(myinput)
        numbers.append(item)

print("Frequencies:")
for num in numbers:
    print(midi_to_freq(num))
