import csv
import random
import datetime
import threading

unsortedList = []

def createDataSet(numberRange):
    unsortedList = []
    #numberRange = 1000000
    unsortedList = random.sample(range(0, numberRange * 1000), numberRange)    
    return unsortedList

def readHell():
    with open('unsortedHell.csv', 'r', newline='') as csvfile:
        csvFile = csv.reader(csvfile)
        for lines in csvFile:
            for line in lines:
                unsortedList.append(int(line))

def readHell2():
    with open('unsortedHell2.csv', 'r', newline='') as csvfile:
        csvFile = csv.reader(csvfile)
        for lines in csvFile:
            for line in lines:
                unsortedList.append(int(line))


def bubbleSort(p_my_array):
    my_array = p_my_array[:]
    print("Starting bubble sort function")
    start = datetime.datetime.now()
    n = len(my_array)
    for i in range(n-1):
        for j in range(n-i-1):
            if my_array[j] > my_array[j+1]:
                my_array[j], my_array[j+1] = my_array[j+1], my_array[j]
    timeSpent = datetime.datetime.now() - start       
    print(timeSpent)
    return my_array

def split(myList):
    midpoint = len(myList) // 2
    list1 = myList[:midpoint]
    list2 = myList[midpoint:]
    return ([list1, list2])

    # Example usage:
    my_list = [1, 2, 3, 4, 5, 6, 7]
    first_half, second_half = split_list(my_list)
    print(f"First half: {first_half}")
    print(f"Second half: {second_half}")

readHell()
#bubbleSort(unsortedList)
#unsortedList = createDataSet(20)
lists = split(unsortedList)
list1 = lists[0]
list2 = lists[1]


t1 = threading.Thread(target=bubbleSort, args=[list1])
t2 = threading.Thread(target=bubbleSort, args=[list2])

t1.start()
t2.start()