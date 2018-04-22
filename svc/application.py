from flask import Flask, request, jsonify
from flask_cors import cross_origin, CORS
import os
import sys
from svc.dbClient import DBClient
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

    result = {}
    for feature in features:
        score = 0
        for weight in weights:
            featureName = weight['feature']
            if featureName == 'intercept':
                score += weight['weight']
            else:
                score += feature[featureName] * weight['weight']
        weights.rewind()

        result[str(feature['timestamp'])] = score

    return jsonify(result)

@app.route('/getDistribution', methods = ['GET'])
def getAverageScoreDistribution():
    averageScores = dbClient.getAverageScoresAll()
    result = {}
    count = {}
    for userScoreAge in averageScores:
        age = userScoreAge['age']
        if age >= 18 and age <= 30:
            result['18-30'] = result.get('18-30', 0) + userScoreAge['score']
            count['18-30'] = count.get('18-30', 0) + 1
        elif age >= 31 and age <= 40:
            result['31-40'] = result.get('31-40', 0) + userScoreAge['score']
            count['31-40'] = count.get('31-40', 0) + 1
        elif age >= 41:
            result['41-'] = result.get('41-', 0) + userScoreAge['score']
            count['41-'] = count.get('41-', 0) + 1

    for k, v in result.items():
        if count[k] != 0:
            result[k] = result[k]/count[k]

    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3034))
    app.run(debug=True, port=port)
