"""
main code for project
"""
import csv
import player

# read data from the "Data.csv" file into a list "DataSet"
with open('Data/Data.csv', newline='') as Data:
    reader = csv.reader(Data)
    DataSet = list(reader)
    DataSet = DataSet[1:] # exclude first row - this is the headings for the data

for row in DataSet:
    currentPlayer = None # current player object

    # keep playerDB up to date
    for existingPlayer in player.playerDB:
        if existingPlayer.name == row[2]:
            existingPlayer.update(row) # update the object with new data
            currentPlayer = existingPlayer
            break
    
    # create a player object from the row in the dataset and add it to the playerDB if it doesn't exist in the playerDB
    else:
        player1 = player.Player(row)
        player.playerDB.append(player1) # add the player to the DB
        currentPlayer = player1
    
    