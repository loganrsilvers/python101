"""1. Problem A (3.75 points)
Write a Python function that contains a loop which:
Asks the user to provide one example for each of the following data types: int, str, bool, float.
Prints out the type of each of the inputs.
Prints an error message if it is of type tuple.
Hint: Use the core Python input(), type(), isinstance(), and eval() functions."""

#Hint: Use the core Python input(), type(), isinstance(), and eval() functions."""

#Write a Python function 
def problemA():
    data_types = ['int', 'str', 'bool', 'float'] #each of the inputs
    #that contains a loop which:
    for data_type in data_types:
        #Asks the user to provide one example for each of the following data types: int, str, bool, float.
        input1 = input(f"provide one example for {data_type}: ") #Prints out the type of each of the inputs.
        #input(),
        inputAfter = eval(input1) #eval()
        #if it is of type tuple.
        if isinstance(inputAfter, tuple): #isinstance(),
            #Prints an error message 
            print("error tuple.")
        else:
            print(f"The type of the input is: {type(inputAfter)}") # type(),
        

#problemA()

"""2. Problem B (3.75 points)
Write a Python function odds() that:

Collects into a list the odd integers in a tuple provided to the function through an input argument.
Prints a message indicating
how many items the input tuple contained and
how many odd integers were found.
Returns the odd integers as list."""

#Write a Python function odds() that:
#Collects into a list the odd integers 
# in a tuple provided to the function 
# through an input argument.
def odds(mytuple): # input argument
    listofints = [] # Collects into a list the odd integers 
    for thingy in mytuple:
        if isinstance(thingy, int) and thingy % 2 != 0: 
            listofints.append(thingy)
    #Prints a message indicating
    #how many items the input tuple contained and
    print(f"input tuple contained {len(mytuple)} many things and")
    #how many odd integers were found.
    print(f"{len(listofints)} odd integers were found.")
    #Returns the odd integers as list."""
    return listofints


#odds((1, 2, 3, 4, 5, 6, 7, 8, 9, 10))

"""3. Problem C (3.75 points)
Write a Python function that accepts a string as an argument and prints a message indicating three things:

How many upper-case letters there are in the string.
How many lower-case letters there are in the string.
How many non-letter characters (such as periods, commas, hashes, carots, spaces etc.) there are in the input string.
Refer to this list of string methodsLinks to an external site.."""


#Write a Python function 
# that accepts a string as an argument 
def problemC(mystring):
    upper = 0
    lower = 0
    etc = 0
    for char in mystring:
        if char.isupper():
            upper += 1
        elif char.islower():
            lower += 1
        else:
            etc += 1
    #and prints a message indicating three things:
            #How many upper-case letters there are in the string.
    print(f" How many upper-case letters there are in the string {upper}")
            #How many lower-case letters there are in the string.
    print(f" How many lower-case letters there are in the string {lower}")
            #How many non-letter characters (such as periods, commas, hashes, carots, spaces etc.) there are in the input string.
    print(f" How many non-letter characters (such as periods, commas, hashes, carots, spaces etc.) there are in the input string {etc}")


#problemC("python PYTHON 1111999000000")

"""4. Problem D (3.75 points)
For each of the three kinds of character in the previous problem, use Python to calculate and print the percentage of each kind of character in the string. For example, your output could look something like:

The string "S hO8sdh uh 0ihaodhv ohs08h0u" contains 29 characters, of which approximately 
-  2 are uppercase letters     ( 6.89%) 
- 18 are lower-case letters    (62.07%) 
-  9 are non-letter characters (31.03%)"""

#what?????
def problemD(mystring):
    upper = 0
    lower = 0
    etc = 0
    for char in mystring:
        if char.isupper():
            upper += 1
        elif char.islower():
            lower += 1
        else:
            etc += 1
    length = len(mystring)
            #The string "S hO8sdh uh 0ihaodhv ohs08h0u" contains 29 characters, of which approximately 
    print(f' The string "{mystring}" contains {length} characters, of which approximately')
            #-  2 are uppercase letters     ( 6.89%) 
    print(f'- {upper} are uppercase letters     ({(upper/length)*100}%)')
            #- 18 are lower-case letters    (62.07%) 
    print(f'- {lower} are lower-case letters    ({(lower/length)*100}%)')
            #-  9 are non-letter characters (31.03%)"""
    print(f'- {etc} are non-letter characters ({(etc/length)*100}%)')

problemD("S hO8sdh uh 0ihaodhv ohs08h0u")