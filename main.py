import csv

import null as null
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import matplotlib.ticker as plticker
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

results = pd.read_csv('matches_new.csv')
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from sklearn import linear_model
from sklearn import datasets
from sklearn.svm import l1_min_c

# get total number of rows
#print("Total no. of rows: %d" % (len(results)))
#print(results[3:].head())
#print(results.head())
#stampiamo chi era il favorito e chi invece ha vinto (o se c'è stato un pareggio)
winner = []
for i in range (len(results['outcome'])):
    if results ['team1_odds'][i] > results['team2_odds'][i]:
        if results['team1_odds'][i] > results['draw_odds'][i]:
            winner.append("1: "+results['team1'][i] + " "+ results['outcome'][i])
    elif results['team1_odds'][i] < results ['team2_odds'][i]:
        if results['team2_odds'][i] > results['draw_odds'][i]:
            winner.append("2: "+results['team2'][i] + " "+ results['outcome'][i])
    else:
        winner.append('Draw' + " "+ results['outcome'][i])
#come parametro per la logistic regression possiamo utilizzare le quotazioni dell' 1,2,X
#selezioniamo solo le colonne che ci interessano

columns = ['team1', 'team2', 'team1_odds', 'team2_odds','draw_odds','outcome']
results = results[columns]
#print(results[columns])
#Costruiamo il modello
#la colonna outcome deve essere di tipo numerico -> TECNICA DI One hot encoding
#1 se pareggio, 2 se vince team1
df_teams = results
df_teams.loc[df_teams.outcome == 'TEAM1','outcome']=2
df_teams.loc[df_teams.outcome == 'DRAW', 'outcome']=1
df_teams.loc[df_teams.outcome == 'TEAM2', 'outcome']=0

#convertiamo team1 e team2 in valori continui
final = pd.get_dummies(df_teams, prefix=['team1', 'team2'], columns=['team1', 'team2'])
# Separatiamo i 2 set X e Y
X = final.drop(['outcome'], axis=1)
y = final["outcome"]
y = y.astype('int')

#Separiamo training set e test set
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42)
#logreg = LogisticRegression()
#logreg.fit(X_train, y_train)
#score = logreg.score(X_train, y_train)
#score2 = logreg.score(X_test, y_test)

#print("Training set accuracy: ", '%.3f'%(score))
#rint("Test set accuracy: ", '%.3f'%(score2))

#utilizziamo adesso i valori delle quote
#i team con quote maggiori saranno considerati favoriti
#calcoliamo la somma delle quote e salviamole su un altro file csv
bets= pd.read_csv('quotes.csv')
prova = bets;
for i in range(len(bets['team'])):
    bets.loc[bets.odds!=0,'odds']=0
for i in range (len(results['outcome'])):
    for j in range(len(bets['team'])):
        if bets['team'][j] ==results['team1'][i]:
         bets.loc[bets.odds!=-0,'odds']= bets['odds'][j]+results["team1_odds"][i]
         if bets['team'][j] == results['team2'][i]:
             bets.loc[bets.odds != -0, 'odds'] = [bets['odds'][j] + results["team2_odds"][i]]
print(bets.head())