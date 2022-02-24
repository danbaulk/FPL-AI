"""this module retrieves the data for the upcoming gameweek of all the players"""
import pandas as pd
import Player
import requests
import csv
import json
from understat import Understat
import asyncio
import aiohttp

# position dictionary
pos_dict = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

# fixture difficulty ratings for 21/22 season
rating2021 = {"Manchester City": 10, "Liverpool": 10, "Chelsea": 9, "West Ham": 9, "Manchester United": 8, "Arsenal": 8, "Tottenham": 7, "Wolves": 7, "Brighton": 6, "Southampton": 6, "Aston Villa": 5, "Leicester": 5, "Crystal Palace": 4,  "Brentford": 4, "Leeds": 3, "Everton": 3, "Newcastle": 2, "Norwich": 2, "Watford": 1, "Burnley": 1}

# team id and team name dictionary
team_dict = {1: "Arsenal", 2: "Aston Villa", 3: "Brentford", 4: "Brighton", 5: "Burnley", 6: "Chelsea", 7: "Crystal Palace", 8: "Everton", 9: "Leicester", 10: "Leeds", 11: "Liverpool", 12: "Manchester City", 13: "Manchester United", 14: "Newcastle", 15: "Norwich", 16: "Southampton", 17: "Tottenham", 18: "Watford", 19: "West Ham", 20: "Wolves"}

# read the understat and FPL id data into a dictionary for faster lookups
with open('id_dict.csv', newline='') as data:
    reader = csv.reader(data)
    dataList = list(reader)
    header = dataList[0] # save the header to be added later
    dataList = dataList[1:] # exclude first row - this is the headings for the data

# key: FPL ID, value: understat ID
id_dict = {}
for row in dataList:
    id_dict[row[1]] = row[0]

def get(url):
    """gets the JSON data from the given URL"""
    response = requests.get(url)
    return json.loads(response.content)

async def getXGI(understat, ID, season):
    """get the expected goals and expected assists of the player"""
    xG = []
    xA = []
    data = await understat.get_player_matches(ID, {"season": str(season)})
    data = data[:4] # get the last 4 games
    for stat in data:
        xG.append(float(stat['xG']))
        xA.append(float(stat['xA']))
    return xG, xA

async def getXGC(understat, team, season):
    """get the expected goals conceded"""
    xGC = []
    data = await understat.get_team_results(team, season)
    data = data[-4:] # get the last 4 games
    for game in data:
        home = game["h"]["title"]
        if (home == team):
            xGC.append(float(game["xG"]["a"]))
        else:
            xGC.append(float(game["xG"]["h"]))
    return xGC

async def main(season, ID, team):
    """return the understat expected stats data"""
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        understatData = await asyncio.gather(getXGI(understat, ID, season), getXGC(understat, team, season))

        xG = understatData[0][0]
        xA = understatData[0][1]
        xGC = understatData[1]
    
        data = [xG, xA, xGC]
        return data

url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
response = get(url)
players = response['elements']


# for each player who is available to play, create a player object and add their details
for player in players:
    if player['status'] == 'a':
        ID = 0
        influence = []
        creativity = []
        threat = []
        ict = []
        performances = []
        xG = []
        xA = []
        xGC = []
        team = 0
        opp = 0
        home = 0

        playerObj = Player.Player()
        playerObj.name = player['first_name'] + " " + player['second_name']
        playerObj.value = player['now_cost']
        playerObj.pos = pos_dict[player['element_type']]
        ID = player['id']
            
        # get their recent FPL performance stats
        url = 'https://fantasy.premierleague.com/api/element-summary/' + str(ID) + '/' 
        response = get(url)
        history = response['history']
        recentGames = history[-4:]

        for game in recentGames:
            influence.append(float(game['influence']))
            creativity.append(float(game['creativity']))
            threat.append(float(game['threat']))
            ict.append(float(game['ict_index']))
            performances.append(int(game['total_points']))
        
        playerObj.avg_I = Player.calcAvg(influence)
        playerObj.avg_C = Player.calcAvg(creativity)
        playerObj.avg_T = Player.calcAvg(threat)
        playerObj.avg_ICT = Player.calcAvg(ict)
        playerObj.form = Player.calcAvg(performances)

        # get their upcoming fixture details
        fixture = response['fixtures'][0]
        if fixture['is_home']:
            opp = fixture['team_a']
            team = fixture['team_h']
            home = 1
        else:
            opp = fixture['team_h']
            team = fixture['team_a']
            home = 0
        team = team_dict[team]
        playerObj.fixture = rating2021[team_dict[opp]]
        playerObj.wasHome = home

        # get their recent understat performance stats
        try:
            season = 2021
            understatID = id_dict[str(ID)]
            loop = asyncio.get_event_loop()
            retrievedData = loop.run_until_complete(main(season, understatID, team))

            playerObj.avg_xG = Player.calcAvg(retrievedData[0])
            playerObj.avg_xA = Player.calcAvg(retrievedData[1])
            playerObj.avg_xGC = Player.calcAvg(retrievedData[2])
        except:
            print("Understat ID not found:", playerObj.name, ID)
            playerObj.avg_xG = 'FAIL'
            playerObj.avg_xA = 'FAIL'
            playerObj.avg_xGC = 'FAIL'

        Player.playerDB.append(playerObj) # add the player to the DB



# with all the players data in the playerDB output it to a file so it can be used by the model
header = ['name', 'pos', 'avg_xG', 'avg_xA', 'avg_xGC', 'avg_I', 'avg_C', 'avg_T', 'avg_ICT', 'fixture_difficulty', 'is_home', 'form']
data = []
for player in Player.playerDB:
    data.append([player.name, player.pos, player.avg_xG, player.avg_xA, player.avg_xGC, player.avg_I, player.avg_C, player.avg_T, player.avg_ICT, player.fixture, player.wasHome, player.form])

with open('retrieved_data2.csv', 'w', encoding="utf-8", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)

    for row in data:
        writer.writerow(row)