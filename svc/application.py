from flask import Flask, request, jsonify
from flask_cors import cross_origin, CORS
import os
import sys
from svc.dbClient import DBClient
import json
from flask import jsonify
from datetime import datetime, timedelta
import googlemaps

app = Flask(__name__)
CORS(app, support_credentials=True)
dbClient = DBClient()
gmaps = googlemaps.Client(key='AIzaSyBAlFTCNMaNX2E2eW2Rt1C-OBFe_LEqCHE')

def getUserScoreWithTimestamp(userId):
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

        result[feature['timestamp']] = score

    return result

def isBetterPathExists(mode, sourceLatitude, sourceLongitude,
                               destinationLatitude, destinationLongitude,
                               distance, time):
    matrix = gmaps.distance_matrix((sourceLatitude, sourceLongitude),
                                   (destinationLatitude, destinationLongitude),
                                   mode=mode)

    if "duration" not in matrix["rows"][0]["elements"][0]:
        return False
    timeBicycle = matrix["rows"][0]["elements"][0]["duration"]["value"]
    distanceBicycle = matrix["rows"][0]["elements"][0]["distance"]["value"]

    # 5min
    if timeBicycle - time < 300:
        return True

    #1 km
    if distance - distanceBicycle < 1000:
        return True

    return False

@app.route('/api/greenscore', methods = ['GET'])
def getGreenScore():
    if request.method == 'GET':
        userId = request.args['userId']

    result = getUserScoreWithTimestamp(userId)

    current = datetime.now()

    totalMonthScore = 0
    totalPreviousScore = 0
    count = 0
    countPrevious = 0
    for timestamp, score in result.items():
        if (current - timestamp).days < 31:
            totalMonthScore += score
            count += 1
        elif (current - timestamp).days < 60 and (current - timestamp).days > 30:
            totalPreviousScore += score
            countPrevious += 1

    score = "NA"
    previousScore = "NA"
    if count != 0:
        score = totalMonthScore/count
    if countPrevious != 0:
        previousScore = totalPreviousScore/countPrevious

    return jsonify({ "score": score, "previousScore": previousScore })

@app.route('/getScores', methods = ['GET'])
def getScores():
    if request.method == 'GET':
        userId = request.args['user_id']

    result = getUserScoreWithTimestamp(userId)

    mainResult = {}
    for timestamp, score in result.keys():
        mainResult[str(timestamp)] = score

    return jsonify(mainResult)

@app.route('/api/gscoredistribution', methods = ['GET'])
def getAverageScoreDistribution():
    averageScores = dbClient.getAverageScoresAll()
    result = {}
    count = {}
    for userScoreAge in averageScores:
        age = userScoreAge['age']
        if age >= 18 and age <= 25:
            result['18-25'] = result.get('18-25', 0) + userScoreAge['score']
            count['18-25'] = count.get('18-25', 0) + 1
        elif age >= 26 and age <= 40:
            result['26-40'] = result.get('26-40', 0) + userScoreAge['score']
            count['26-40'] = count.get('26-40', 0) + 1
        elif age >= 41 and age <= 50:
            result['41-50'] = result.get('41-50', 0) + userScoreAge['score']
            count['41-50'] = count.get('41-50', 0) + 1
        elif age >= 51 and age <= 65:
            result['51-65'] = result.get('51-65', 0) + userScoreAge['score']
            count['51-65'] = count.get('51-65', 0) + 1
        elif age >= 66:
            result['66+'] = result.get('66+', 0) + userScoreAge['score']
            count['66+'] = count.get('66+', 0) + 1

    for k, v in result.items():
        if count[k] != 0:
            result[k] = result[k]/count[k]

    return jsonify(result)

@app.route('/api/factors', methods = ['GET'])
def getFactors():
    if request.method == 'GET':
        userId = request.args['userId']

    features = dbClient.getFeatures(userId)

    revCount = 0
    onCall = 0
    numBikes = 0
    publicTransport = 0

    for feature in features:
        if (datetime.now() - feature['timestamp']).days >= 31:
            continue
        revCount += feature['accelerometer'] * 10
        onCall += feature['isOnCall']
        if isBetterPathExists('bicycling', feature['sourceLatitude'], feature['sourceLongitude'],
                                      feature['destinationLatitude'], feature['destinationLongitude'],
                                      feature['distance'] * 1000000, feature['timeInSeconds'] * (timedelta(hours=10).seconds)):
            numBikes += 1

        if isBetterPathExists('transit', feature['sourceLatitude'], feature['sourceLongitude'],
                              feature['destinationLatitude'], feature['destinationLongitude'],
                              feature['distance'] * 1000000, feature['timeInSeconds'] * (timedelta(hours=10).seconds)):
            publicTransport += 1

    return jsonify({
        'revCount': int(revCount),
        'onCall': onCall,
        'numBikes': numBikes,
        'publicTransport': publicTransport
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3034))
    app.run(debug=True, port=port)
