import numpy as np
import pandas as pd
import re
import csv
import datetime
dateFunction = datetime.datetime.now()

date = (dateFunction.strftime("%Y-%m-%d"))
#Order of events:
#1. Input both lists
dfDK = pd.read_csv (r'NHLDKSALARIES'+ date + '.csv')   #read the csv file (put 'r' before the path string to address any special characters in the path, such as '\'). Don't forget to put the file name at the end of the path + ".csv"
dfNHL = pd.read_csv (r'NHLDK' + date + '.csv')   #read the csv file (put 'r' before the path string to address any special characters in the path, such as '\'). Don't forget to put the file name at the end of the path + ".csv"
#row_countDK = sum(1 for row in dfDK)
csvFileName = 'NHL&DKStats' + date + '.csv'

#2. For each player in dfDK, find the player with the same name in dfNHL.
#Then append the salary of that player in dfDK to the 11th column.
dfDKi = 0 
dfNHLi = 0
#print(dfDK.FullName[dfDKi])
#print(dfNHL.PlayerName[dfNHLi])
playerSalaryMap = {}

# {
#     "Sidney Crosby" : "8500",
#     "Elias Petterson": "20"
# }

for index, row in dfDK.iterrows():
    playerSalaryMap[row.FullName] = row.Salary

salaries = []
for index, row in dfNHL.iterrows():
    if row.PlayerName in playerSalaryMap:
        salaries.append(playerSalaryMap[row.PlayerName])
        #print(row)
    else:
        salaries.append("")
        print("player not found" + " " + str(row.PlayerName))
#print(salaries)

dfNHL["Salary"] = salaries
print(dfNHL)

dfNHL.to_csv(csvFileName)
    


