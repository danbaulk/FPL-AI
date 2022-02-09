import pandas as pd
import requests
import json
from understat import Understat
import asyncio
import aiohttp

def get(url):
    response = requests.get(url)
    return json.loads(response.content)



# get the current player statistics
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'

response = get(url)
players = response['elements']
teams = response['teams']
events = response['events']
players_df = pd.DataFrame(players) # current player data
teams_df = pd.DataFrame(teams) # current teams data
events_df = pd.DataFrame(events) # gameweek data
events_df['deadline_time'] = pd.to_datetime(events_df['deadline_time'])
events_df['deadline_time'] = events_df['deadline_time'].dt.tz_localize(None)

#players_df.to_csv('players.csv')



# get a players history and fixtures
player_id = 16
url = 'https://fantasy.premierleague.com/api/element-summary/' + str(player_id) + '/' 

response = get(url)
fixtures = response['fixtures']
history = response['history']
history_past = response['history_past']
fixtures_df = pd.DataFrame(fixtures) # fixtures data for a player
history_df = pd.DataFrame(history) # player history for this season
history_past_df = pd.DataFrame(history_past) # players history over past few seasons

#history_df.to_csv('history.csv')
#fixtures_df.to_csv('fixtures.csv')



# get the players understat data
season = "2021"
ID = "8089" # using the id_dict
team = "Arsenal"

async def getXGI(understat, ID, season):
    """get the expected goals and expected assists of the player"""
    data = await understat.get_player_matches(ID, {"season": season})
    xG = data
    xA = data
    return xG, xA

async def getXGC(understat, team, season):
    """get the expected goals conceded"""
    data = await understat.get_team_results(team, season)
    xGC = data
    return xGC

async def main():
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        understatData = await asyncio.gather(getXGI(understat, ID, season), getXGC(understat, team, season))
        xG = understatData[0][0]
        xA = understatData[0][1]
        xGC = understatData[1]
    
        data = [xG, xA, xGC]
        return data

loop = asyncio.get_event_loop()
retrievedData = loop.run_until_complete(main())

print(retrievedData[0][:4])
print(" ")
print(retrievedData[1][:4])
print(" ")
print(retrievedData[2][:4])