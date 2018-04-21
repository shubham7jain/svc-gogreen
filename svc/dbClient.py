from mongo_connect import connectMongo

class DBClient:
    def __init__(self):
        self.db = connectMongo()
        self.userFeatures = self.db['user_features']
        self.weights = self.db['weights']

    def getFeatures(self, user_id):
        result = self.userFeatures.find({
            'user_id': user_id
        })

        return result

    def getWeights(self):
        result = self.weights.find()
        return result