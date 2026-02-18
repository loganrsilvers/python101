#Zero crossing: 

# The script should contain a function that does the splitting.
def func(nums):
    for num in range(1, len(nums)):
        # splits the list at the first instance the number changes sign 
        if (nums[num-1] >= 0 and nums[num] < 0):
            # https://pieriantraining.com/what-does-mean-in-python-a-guide-to-slicing/
            return nums[:num]
        elif (nums[num-1] < 0 and nums[num] >= 0):
            return nums[:num]
    return nums
    
# asks the user to enter a list of numbers 
myinput = input("enter a list of numbers separated by spaces: ")

# splits the list 
numbers = []
for num in myinput.split():
    numbers.append(int(num))

#  and prints the first portion of the list. 
print(func(numbers))

