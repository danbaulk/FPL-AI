"""
run this script to update the form in the data.csv
this script will only need to be run once, in order to update the csv file
"""
import csv
import player
import asyncio
import json
import aiohttp
from understat import Understat

# dictionary matching names to understat IDs
name_id = {}

async def getID(understat, season, name):
    """get the understat ID of the player"""
    if (name in name_id):
        ID = name_id[name]
    else:
        data = await understat.get_league_players("epl", season, player_name = name)
        ID = data[0]["id"] # add the name and id to the dictionary for quicker lookups
        name_id[name] = ID
    return ID

async def getXGI(understat, ID, season, date):
    """get the expected goals and expected assists of the player"""
    data = await understat.get_player_matches(ID, {"season": str(season), "date": date})
    xG = data[0]["xG"]
    xA = data[0]["xA"]
    return xG, xA

async def getXGC(understat, fixture, season, date):
    """get the expected goals conceded"""
    data = await understat.get_team_results(fixture, season)
    for game in data:
        USdate = game["datetime"]
        if date in USdate:
            data = game

    home = data["h"]["title"]
    if (home == fixture):
        xGC = data["xG"]["h"]
    else:
        xGC = data["xG"]["a"]
    return xGC

async def main(season, name, dateTime, fixture):
    """attempt to get the understat data of the player"""
    async with aiohttp.ClientSession() as session:
        success = True
        ID = ['0']
        stats = [('0', '0'), '0']
        understat = Understat(session)
        date = dateTime[0]

        try:
            ID = await asyncio.gather(getID(understat, season, name))
            stats = await asyncio.gather(getXGI(understat, ID[0], season, date), getXGC(understat, fixture, season, date))
        except:
            success = False

        return ID[0], stats[0][0], stats[0][1], stats[1], success


# read data from the specifed file into a list called DataSet
with open('Data/CleanedData.csv', newline='') as Data:
    reader = csv.reader(Data)
    DataSet = list(reader)
    header = DataSet[0] # save the header to be added later
    DataSet = DataSet[1:] # exclude first row - this is the headings for the data
    count = 0

# for each row in the DataSet calculate form 
for row in DataSet:
    currentPlayer = None # current player object
    success = True # whether or not the understat data could be retrieved

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

    # if the player plays in the game get their understat data
    if (row[17] != "0"):
        loop = asyncio.get_event_loop()
        understatData = loop.run_until_complete(main(currentPlayer.season, currentPlayer.name, currentPlayer.date, currentPlayer.fixture))
        
        # using the current player and row, add the supplemented data to the row
        # only add the data if the understat data could be retrieved
        success = understatData[4]
        if (success):
            currentPlayer.ID = understatData[0]
            currentPlayer.xG = understatData[1]
            currentPlayer.xA = understatData[2]
            currentPlayer.xGC = understatData[3]

            row.extend([currentPlayer.form, currentPlayer.xG, currentPlayer.xA, currentPlayer.xGC, currentPlayer.ID])
            count = count + 1
            print (count)
        else:
            # if the understat data couldnt be retrieved, remove the row
            DataSet.remove(row)


# once the DataSet has been updated, write it to a csv file
with open('UpdatedData.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header.append('form', 'xG', 'xA', 'xGC', 'ID')
    writer.writerow(header)

    for row in DataSet:
        writer.writerow(row)