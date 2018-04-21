from flask import Flask, request, jsonify
from flask_cors import cross_origin, CORS
import os
import sys
from dbClient import DBClient
import json
from flask import jsonify

app = Flask(__name__)
CORS(app, support_credentials=True)
dbClient = DBClient()

@app.route('/getScores', methods = ['GET'])
def getScores():
    if request.method == 'GET':
        userId = request.args['user_id']
    features = dbClient.getFeatures(userId)
    weights = dbClient.getWeights()

    result = []
    result = {}
    for feature in features:
        score = 0
        for weight in weights:
            featureName = weight['feature']
            score += feature[featureName] * weight['weight']
        weights.rewind()

        result[str(feature['timestamp'])] = score

    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3034))
    app.run(debug=True, port=port)
