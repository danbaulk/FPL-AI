"""
run this script to the csv file with supplementary data
this script will only need to be run once, in order to update the csv file
"""
import csv
import player
import asyncio
import json
import aiohttp
from understat import Understat

async def getID(understat, season, name):
    """get the understat ID of the player"""
    data = await understat.get_league_players("epl", season, player_name = name)
    ID = data[0]["id"] 
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

async def main(data):
    """attempt to get the understat data of the player and calculate form"""
    async with aiohttp.ClientSession() as session:
        currentPlayer = None # current player object   
        previousForm = 0 # the players form going into this game

        # keep playerDB up to date
        for existingPlayer in player.playerDB:
            if existingPlayer.name == data[2]:
                previousForm = existingPlayer.form # update the form to be their form going into this game
                existingPlayer.update(data) # update the object with new data
                currentPlayer = existingPlayer
                break
    
        # create a player object from the row in the dataset and add it to the playerDB if it doesn't exist in the playerDB
        else:
            player1 = player.Player(data)
            player.playerDB.append(player1) # add the player to the DB
            currentPlayer = player1

        understat = Understat(session)
        date = currentPlayer.date[0]

        try:
            ID = await asyncio.gather(getID(understat, currentPlayer.season, currentPlayer.name))
            understatData = await asyncio.gather(getXGI(understat, ID[0], currentPlayer.season, date), getXGC(understat, currentPlayer.fixture, currentPlayer.season, date))
            currentPlayer.ID = ID[0]
            currentPlayer.xG = understatData[0][0]
            currentPlayer.xA = understatData[0][1]
            currentPlayer.xGC = understatData[1]
        except:
            currentPlayer.ID = 'FAIL'
            currentPlayer.xG = 'FAIL'
            currentPlayer.xA = 'FAIL'
            currentPlayer.xGC = 'FAIL'
        
        data.extend([currentPlayer.xG, currentPlayer.xA, currentPlayer.xGC, currentPlayer.ID, previousForm])
        return data


# read data from the specifed file into a list called DataSet
with open('Data/CleanedData.csv', newline='') as Data:
    reader = csv.reader(Data)
    DataSet = list(reader)
    header = DataSet[0] # save the header to be added later
    DataSet = DataSet[1:] # exclude first row - this is the headings for the data

# limit the number of simultaneous API calls
sem = asyncio.Semaphore(20)
async def safe_main(row):
    async with sem:  # semaphore limits num of simultaneous API calls
        return await asyncio.gather(main(row))

async def getUSdata():
    tasks = []
    for row in DataSet:
        tasks.append(asyncio.ensure_future(safe_main(row)))

    updatedData = await asyncio.gather(*tasks)
    return updatedData
            
loop = asyncio.get_event_loop()
updatedData = loop.run_until_complete(getUSdata())


# once the DataSet has been updated, write it to a csv file
with open('UpdatedData.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header.extend(['xG', 'xA', 'xGC', 'ID', 'Form'])
    writer.writerow(header)

    for row in updatedData:
        writer.writerow(row[0])
