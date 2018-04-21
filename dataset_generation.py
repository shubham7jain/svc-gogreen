import random
from datetime import datetime, timedelta
import time

def randomDate(start, end):
    frmt = '%d-%m-%Y %H:%M'

    stime = time.mktime(time.strptime(start, frmt))
    etime = time.mktime(time.strptime(end, frmt))

    ptime = stime + random.random() * (etime - stime)
    dt = datetime.fromtimestamp(time.mktime(time.localtime(ptime)))
    return dt

def onCallScore(isOncall):
    if isOnCall:
        return [-0.6, -0.4]
    else:
        return 0.2

def accelerometerScore(accelerometer):
    return -accelerometer

def distanceScore(distance):
    return distance

def timeScore(time):
    return -time * 0.6

def calculateScore(accelerometer, timeInSeconds, distance, isCar, isOnCall):
    score = 0
    score = onCallScore(isOnCall) + accelerometerScore(accelerometer) + distanceScore(distance) + timeScore(timeInSeconds)

    score += 2.1
    score = score/3.3

    return score*100

dataset_size = 100
for i in range(dataset_size):
    accelerometer = random.randint(0, 100)/100
    startTimestamp = randomDate("01-01-2013 00:00", "31-12-2013 11:59")
    endTimestamp = startTimestamp + timedelta(hours=(round(random.uniform(0, 8), 2)))
    distance = ((random.uniform(0, 2)) * ((endTimestamp - startTimestamp).seconds)/60)/(2*timedelta(hours=8).seconds/60)
    timeInSeconds = ((endTimestamp - startTimestamp).seconds)/(timedelta(hours=8).seconds)
    isCar = random.randint(0, 1)
    isOnCall = random.randint(0, 1)
    print(accelerometer, timeInSeconds, distance, isCar, isOnCall)
    score = calculateScore(accelerometer, timeInSeconds, distance, isCar, isOnCall)
    print(score)