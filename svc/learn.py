from sklearn.linear_model import LinearRegression
import pandas as pd
from dbClient import DBClient

dbClient = DBClient()
df = pd.read_csv('train.txt')

model = LinearRegression()

# print(df[['accelerometer', 'timeInSeconds', 'distance', 'isOnCall']])
# print(df['score'])
model.fit(df[['accelerometer', 'timeInSeconds', 'distance', 'isOnCall']], df['score'])

dbClient.insertWeights({
    'accelerometer': model.coef_[0],
    'timeInSeconds': model.coef_[1],
    'distance': model.coef_[2],
    'isOnCall': model.coef_[3],
    'intercept': model.intercept_
})

dbClient.updateAvgScoreForUsers()