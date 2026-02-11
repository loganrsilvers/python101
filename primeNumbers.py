def is_prime(num):
    if num < 2:
        return False
    for i in range(2, num):
    #for (int i = 2; i < num; i++)
        if num % i == 0:
            return False
    return True

for num in range(1, 101):
# same as up there ^^ its like 
#for (int num = 1; num < 101; num++)
    if is_prime(num):
        print(num)









for everyNumber in range(1, 101):
    for numberweAreat in range(1, everyNumber):
        if everyNumber % numberweAreat == 0:
            break
        else:
            print(everyNumber)   