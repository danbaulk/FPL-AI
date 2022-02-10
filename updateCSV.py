"""
run this script to the csv file with supplementary data
this script will only need to be run once, in order to update the csv file
"""
import csv
import Player
import asyncio
import aiohttp
from understat import Understat

# the fixture difficulty dictionaries
rating2016 = {"Chelsea": 10, "Tottenham": 10, "Manchester City": 9, "Liverpool": 9, "Arsenal": 8, "Manchester United": 8, "Everton": 7 , "Southampton": 7, "Bournemouth": 6, "West Bromwich Albion": 6, "West Ham": 5, "Leicester": 5, "Stoke": 4, "Crystal Palace": 4, "Swansea": 3, "Burnley": 3, "Watford": 2, "Hull": 2, "Middlesbrough": 1, "Sunderland": 1}
rating2017 = {"Manchester City": 10, "Manchester United": 10, "Tottenham": 9, "Liverpool": 9, "Chelsea": 8, "Arsenal": 8, "Burnley": 7, "Everton": 7, "Leicester": 6, "Newcastle": 6, "Crystal Palace": 5, "Bournemouth": 5, "West Ham": 4,  "Watford": 4, "Brighton": 3, "Huddersfield": 3, "Southampton": 2, "Swansea": 2, "Stoke": 1, "West Bromwich Albion": 1}
rating2018 = {"Manchester City": 10, "Liverpool": 10, "Chelsea": 9, "Tottenham": 9, "Arsenal": 8, "Manchester United": 8, "Wolves": 7, "Everton": 7, "Leicester": 6, "West Ham": 6, "Watford": 5, "Crystal Palace": 5, "Newcastle": 4,  "Bournemouth": 4, "Burnley": 3, "Southampton": 3, "Brighton": 2, "Cardiff": 2, "Fulham": 1, "Huddersfield": 1}
rating2019 = {"Liverpool": 10, "Manchester City": 10, "Manchester United": 9, "Chelsea": 9, "Leicester": 8, "Tottenham": 8, "Wolves": 7, "Arsenal": 7, "Sheffield Utd": 6, "Burnley": 6, "Southampton": 5, "Everton": 5, "Newcastle": 4,  "Crystal Palace": 4, "Brighton": 3, "West Ham": 3, "Aston Villa": 2, "Bournemouth": 2, "Watford": 1, "Norwich": 1}
rating2020 = {"Manchester City": 10, "Manchester United": 10, "Liverpool": 9, "Chelsea": 9, "Leicester": 8, "West Ham": 8, "Tottenham": 7, "Arsenal": 7, "Leeds": 6, "Everton": 6, "Aston Villa": 5, "Newcastle": 5, "Wolves": 4,  "Crystal Palace": 4, "Southampton": 3, "Brighton": 3, "Burnley": 2, "Fulham": 2, "West Bromwich Albion": 1, "Sheffield Utd": 1}

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
        # the players average stats going into this game starts off as 0
        form = avg_xG = avg_xA = avg_xGC = avg_I = avg_C = avg_T = avg_ICT = 0 

        # get the players new understat stats
        understat = Understat(session)
        date = data[16][:-1].split("T")[0]
        season = data[1][:4]
        name = data[2]
        fixture = data[19]
        ID = 0
        xG = 0
        xA = 0
        xGC = 0

        try:
            ID = await asyncio.gather(getID(understat, season, name))
            understatData = await asyncio.gather(getXGI(understat, ID[0], season, date), getXGC(understat, fixture, season, date))
            ID = ID[0]
            xG = float(understatData[0][0])
            xA = float(understatData[0][1])
            xGC = float(understatData[1])

            # check the player exists in the DB, if so get their old averages and update it
            for existingPlayer in Player.playerDB:
                if existingPlayer.name == name:
                    # save the players current averages to the local variables 
                    form = existingPlayer.form
                    avg_xG = existingPlayer.avg_xG
                    avg_xA = existingPlayer.avg_xA
                    avg_xGC = existingPlayer.avg_xGC
                    avg_I = existingPlayer.avg_I
                    avg_C = existingPlayer.avg_C
                    avg_T = existingPlayer.avg_T
                    avg_ICT = existingPlayer.avg_ICT

                    # update the object with new data
                    existingPlayer.update(data) 
                    existingPlayer.xG = Player.addRecentStats(existingPlayer.xG, xG)
                    existingPlayer.xA = Player.addRecentStats(existingPlayer.xA, xA)
                    existingPlayer.xGC = Player.addRecentStats(existingPlayer.xGC, xGC)
                    existingPlayer.updateAvgs() # update the averages

                    currentPlayer = existingPlayer
                    break
        
            # if they dont exist create a player object
            else:
                player1 = Player.Player(data)
                Player.playerDB.append(player1) # add the player to the DB
                currentPlayer = player1
                # add the players understat data and calculate their average stats
                currentPlayer.ID = ID
                currentPlayer.xG = [xG]
                currentPlayer.xA = [xA]
                currentPlayer.xGC = [xGC]
                currentPlayer.updateAvgs()

            # switch case for season, replaces the fixture name with fixture difficulty using appropriate dictionary
            if currentPlayer.season == "2016":
                currentPlayer.fixture = rating2016[fixture]
            elif currentPlayer.season == "2017":
                currentPlayer.fixture = rating2017[fixture]
            elif currentPlayer.season == "2018":
                currentPlayer.fixture = rating2018[fixture]
            elif currentPlayer.season == "2019":
                currentPlayer.fixture = rating2019[fixture]
            elif currentPlayer.season == "2020":
                currentPlayer.fixture = rating2020[fixture]
            else:
                print("Name mismatch")
            
            # convert home or away boolean to 1 or 0
            h_a = 1
            if currentPlayer.wasHome == "FALSE":
                h_a = 0
            
            data.extend([ID, xG, avg_xG, xA, avg_xA, xGC, avg_xGC, form, currentPlayer.fixture, h_a, avg_I, avg_C, avg_T, avg_ICT])

        except:
            # if there is missing understat data then we do not process this data entry
            data.extend(['FAIL'])
        
        return data

# read data from the specifed file into a list called DataSet
with open('Data/CleanedDataBlanks.csv', newline='') as Data:
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
    header.extend(['ID', 'xG', 'avg_xG', 'xA', 'avg_xA', 'xGC', 'avg_xGC', 'form', 'fixture_difficulty', 'was_home', 'avg_I', 'avg_C', 'avg_T', 'avg_ICT'])
    writer.writerow(header)

    for row in updatedData:
        writer.writerow(row[0])