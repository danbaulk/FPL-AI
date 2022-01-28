"""
run this script to update the form in the data.csv
this script will only need to be run once, in order to update the csv file
"""
import csv
import player

# read data from the specifed file into a list called DataSet
with open('Data/Data.csv', newline='') as Data:
    reader = csv.reader(Data)
    DataSet = list(reader)
    header = DataSet[0] # save the header to be added later
    DataSet = DataSet[1:] # exclude first row - this is the headings for the data

# for each row in the DataSet calculate form 
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
    
    # using the current player and row, add the form value to the row
    row.append(currentPlayer.form)


# once the DataSet has been updated, write it to a csv file
with open('UpdatedData.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header.append('form')
    writer.writerow(header)

    for row in DataSet:
        writer.writerow(row)