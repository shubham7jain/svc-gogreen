from svc.mongo_connect import connectMongo

class DBClient:
    def __init__(self):
        self.db = connectMongo()
        self.userFeatures = self.db['user_features']
        self.weights = self.db['weights']
        self.userAverageScores = self.db['averageScore']

    def getFeatures(self, user_id):
        result = self.userFeatures.find({
            'user_id': user_id
        })

        return result

    def getWeights(self):
        result = self.weights.find()
        return result

    def getAverageScoresAll(self):
        result = self.userAverageScores.find()
        return result

    def insertEntry(self, userId, latitude1, longitude1, latitude2, longitude2, accelerometer, startTimestamp, endTimestamp,
                                 distance, timeInSeconds, isCar, isOnCall):
        self.userFeatures.insert({
            'timestamp': startTimestamp,
            'user_id': userId,
            'sourceLatitude': latitude1,
            'sourceLongitude': longitude1,
            'destinationLatitude': latitude2,
            'destinationLongitude': longitude2,
            'accelerometer': accelerometer,
            'startTimestamp': startTimestamp,
            'endTimestamp': endTimestamp,
            'distance': distance,
            'timeInSeconds': timeInSeconds,
            'isCar': isCar,
            'isOnCall': isOnCall
        })

    def insertWeights(self, weightsMap):
        for feature, weight in weightsMap.items():
            self.weights.update({'feature': feature}, { '$set': { 'weight': weight }}, True)