import random
from datetime import datetime, timedelta
import time
import googlemaps
from dbClient import DBClient

dbClient = DBClient()
gmaps = googlemaps.Client(key='AIzaSyBfn8jQ8prjOk8V4d68qoe85C3l4hKJeXQ')
def randomDate(start, end):
    frmt = '%d-%m-%Y %H:%M'

    stime = time.mktime(time.strptime(start, frmt))
    etime = time.mktime(time.strptime(end, frmt))

    ptime = stime + random.random() * (etime - stime)
    dt = datetime.fromtimestamp(time.mktime(time.localtime(ptime)))
    return dt

def getTimeDistanceFromGoogle(latitude1, longitude1, latitude2, longitude2):
    matrix = gmaps.distance_matrix((latitude1, longitude1), (latitude2, longitude2))
    return matrix["rows"][0]["elements"][0]["duration"]["value"], matrix["rows"][0]["elements"][0]["distance"]["value"]

def onCallScore(isOncall):
    if isOncall:
        return random.uniform(-0.6, -0.5)
    else:
        return random.uniform(0.1, 0.2)

def accelerometerScore(accelerometer):
    return random.uniform(-1, -0.9) * accelerometer

def distanceScore(distance):
    return random.uniform(0.4, 0.9) * distance

def timeScore(time):
    return -time * random.uniform(0.5, 0.6)

def calculateScore(accelerometer, timeInSeconds, distance, isCar, isOnCall):
    score = onCallScore(isOnCall) + accelerometerScore(accelerometer) + distanceScore(distance) + timeScore(timeInSeconds)

    score += 2.1
    score = score/3.2

    return score*100

def generateAttributeValues(startTime, endTime):
    accelerometer = random.randint(0, 10) / 10

    ### Chances of generating the short trips and long trips should be half and half
    latitude1, longitude1 = random.uniform(32.954039, 33.926300), random.uniform(-97.40845, -90.529583)
    latitude2, longitude2 = random.uniform(32.954039, 33.926300), random.uniform(-97.40845, -90.529583)
    if random.uniform(0, 1) < 0.5:
        latitude1, longitude1 = random.uniform(32.76, 32.80), random.uniform(-96.84, -96.74)
        latitude2, longitude2 = random.uniform(32.76, 32.80), random.uniform(-96.84, -96.74)

    approxTime, approxDistance = getTimeDistanceFromGoogle(latitude1, longitude1, latitude2, longitude2)

    startTimestamp = randomDate(startTime, endTime)
    endTimestamp = startTimestamp + timedelta(
        seconds=(round(random.uniform(approxTime - approxTime / 5, approxTime + approxTime / 5), 1)))

    distance = random.uniform(approxDistance - approxDistance / 5, approxDistance + approxDistance / 5)

    ## Normalizing everything from 0 to 1
    distance = distance / (900000)
    timeInSeconds = ((endTimestamp - startTimestamp).seconds) / (timedelta(hours=9).seconds)

    isCar = random.randint(0, 1)
    isOnCall = random.randint(0, 1)

    return latitude1, longitude1, latitude2, longitude2, accelerometer, startTimestamp, endTimestamp, distance, timeInSeconds, isCar, isOnCall

def generateTrainingData():
    dataset_size = 1000
    for i in range(dataset_size):
        latitude1, longitude1, latitude2, longitude2, accelerometer, startTimestamp, endTimestamp, \
        distance, timeInSeconds, isCar, isOnCall = generateAttributeValues("01-01-2013 00:00", "31-12-2013 11:59")

        score = calculateScore(accelerometer, timeInSeconds, distance, isCar, isOnCall)
        print(accelerometer,',',timeInSeconds,',',distance,',',isCar,',',isOnCall,',',score)

def insertTestData():
    userIdAgeMap = {'1234': 90,
               '2345': 64,
               '3456': 80,
               '4567': 37,
               '5678': 18,
               '6789': 33,
               '7890': 64
               }
    for userId, age in userIdAgeMap.items():
        dbClient.updateAgeForUsers(userId, age)
        for i in range(10):
            latitude1, longitude1, latitude2, longitude2, accelerometer, startTimestamp, endTimestamp, \
            distance, timeInSeconds, isCar, isOnCall = generateAttributeValues("01-03-2018 00:00", "18-04-2018 11:59")

            dbClient.insertFeature(userId, latitude1, longitude1, latitude2, longitude2, accelerometer, startTimestamp, endTimestamp,
                                 distance, timeInSeconds, isCar, isOnCall)



# generateTrainingData()
insertTestData()