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

async def main(season, name, dateTime, fixture):
    """given the season, player name and date of the match, return the players xG, xA and teams xGC"""
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)

        date = dateTime[0]

        # get understat ID of a player name
        # returns an empty list if the name is not found
        data = await understat.get_league_players("epl", season, player_name = name)
        ID = data[0]["id"]
        
        # get xG and xA for a player in a given match
        data = await understat.get_player_matches(ID, {"season": str(season), "date": date})
        xG = data[0]["xG"]
        xA = data[0]["xA"]

        # get xGC for a team in a given match
        data = await understat.get_team_results(fixture, season)
        # dateTime and understat datetime sometimes disagree on exact kickoff time, fix by comparing the date
        for game in data:
            USdate = game["datetime"]
            if date in USdate:
                data = game

        home = data["h"]["title"]

        if (home == fixture):
            xGC = data["xG"]["h"]
        else:
            xGC = data["xG"]["a"]
        
        print(count)

        return xG, xA, xGC


# read data from the specifed file into a list called DataSet
with open('Data/NewNames.csv', newline='') as Data:
    reader = csv.reader(Data)
    DataSet = list(reader)
    header = DataSet[0] # save the header to be added later
    DataSet = DataSet[1:] # exclude first row - this is the headings for the data

    count = 0

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

    # if the player plays in the game get their understat data
    if (row[17] != "0"):
        loop = asyncio.get_event_loop()
        understatData = loop.run_until_complete(main(currentPlayer.season, currentPlayer.name, currentPlayer.date, currentPlayer.fixture))

        currentPlayer.xG = understatData[0]
        currentPlayer.xA = understatData[1]
        currentPlayer.xGC = understatData[2]

    # using the current player and row, add the form value to the row
    row.extend([currentPlayer.form, currentPlayer.xG, currentPlayer.xA, currentPlayer.xGC])

    count = count + 1


# once the DataSet has been updated, write it to a csv file
with open('UpdatedData.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header.append('form', 'xG', 'xA', 'xGC')
    writer.writerow(header)

    for row in DataSet:
        writer.writerow(row)