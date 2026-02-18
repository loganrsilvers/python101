#Define a function that takes a 
# fundamental frequency 
# and 
# number of harmonics
def harmonic_frequencies(myfreq, numHarmonics):
    harmonicsList = []
    # and returns the frequencies of the harmonics as a list.
    for n in range(1, numHarmonics + 1):
        harmonicsList.append(myfreq * n)
    return harmonicsList

print(harmonic_frequencies(190, 5)) 

