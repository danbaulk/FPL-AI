"""
main code for project
"""

import csv
import player

# read data from the "Data.csv" file into a list "DataSet"
with open('Data.csv', newline='') as Data:
    reader = csv.reader(Data)
    DataSet = list(reader)
    DataSet = DataSet[1:] # Exclude first row - this is the headings for the data


player1 = player.Player(DataSet[0])
print(player1.name)