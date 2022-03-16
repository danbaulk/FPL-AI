"""the team selector script will take as input players which want to be included in the team: determined by the 
model to be players who will likely score highly this upcoming gameweek and then output a team which is valid within the FPL 
team creation rules."""

# FPL team rules:
# Budget canot exceed 100m
# No more than 3 players from the same club
# A squad consists of 2 GKs, 5 DEFs, 5 MIDs, 3 FWDs
# Starting 11 must have 1 GK, at least 2 DEFs, at least 2 MIDs and at least 1 FWD. No more than 11 players
# Players not in the starting 11 are on the bench and are ordered in terms of substitution priority

import csv
import requests
import json
import Player

team_dict = {1: "Arsenal", 2: "Aston Villa", 3: "Brentford", 4: "Brighton", 5: "Burnley", 6: "Chelsea", 7: "Crystal Palace", 8: "Everton", 9: "Leicester", 10: "Leeds", 11: "Liverpool", 12: "Manchester City", 13: "Manchester United", 14: "Newcastle", 15: "Norwich", 16: "Southampton", 17: "Tottenham", 18: "Watford", 19: "West Ham", 20: "Wolves"}

# create the team which with the highest confidence of scoring points which is within the FPL rules
budget = 1000
squad = [] # 15 man squad
GK = [] # 2 GK
DEF = [] # 5 DEF
MID = [] # 5 MID
FWD = [] # 3 FWD
startingXI = [] # the selected starting 11
bench = [] # 4 on the bench
# maintain a count of the number of players in each club
count = {"Arsenal": 0, "Aston Villa": 0, "Brentford": 0, "Brighton": 0, "Burnley": 0, "Chelsea": 0, "Crystal Palace": 0, "Everton": 0, "Leicester": 0, "Leeds": 0, "Liverpool": 0, "Manchester City": 0, "Manchester United": 0, "Newcastle": 0, "Norwich": 0, "Southampton": 0, "Tottenham": 0, "Watford": 0, "West Ham": 0, "Wolves": 0}

def checkValid(player):
    """pass the function a player to see if they fit in the squad without breaking FPL rules"""
    valid = True
    pos = player[0].pos
    price = player[0].value
    club = player[0].club

    # check starting 11 isnt full
    if len(squad) == 15:
        valid = False

    # check the positions havent already been filled
    if pos == "GK":
        if len(GK) == 2:
            valid = False
    elif pos == "DEF":
        if len(DEF) == 5:
            valid = False
    elif pos == "MID":
        if len(MID) == 5:
            valid = False
    else:
        if len(FWD) == 3:
            valid = False
    
    # check that the player is within budget
    if price > budget:
        valid = False
    
    # check there arent already 3 players from that club
    if count[club] == 3:
        valid = False

    return valid

def get(url):
    """gets the JSON data from the given URL"""
    response = requests.get(url)
    return json.loads(response.content)

# the input file contains all the players the model predicted would score highly this gameweek along with their confidence
with open('team_candidates.csv', newline='') as data:
    reader = csv.reader(data)
    candidates = list(reader)
    candidates = candidates[1:] # exclude first row - this is the headings for the data

# a list of player objects and their asociated confidence of scoring highly
processedCandidates = []

url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
response = get(url)
FPL_players = response['elements']

# for each player who is in the candidates list, create a player object for them with their relevant data saved in the object variables
for player in FPL_players:
        currentPlayer = Player.Player()
        currentPlayer.name = player['first_name'] + " " + player['second_name']
        currentPlayer.value = player['now_cost']
        currentPlayer.club = team_dict[player['team']]

        # check if the FPL player is in the candidates list by matching their names
        for candidate in candidates:
            if currentPlayer.name == candidate[0]:
                # if the player is a candidate then we store them in the processed candidates list
                currentPlayer.pos = candidate[1]
                confidence = candidate[2]
                processedCandidates.append([currentPlayer, confidence]) # add the player object and their confidence score to the list


# sort the processed candidates list by their confidence
sortedCandidates = sorted(processedCandidates, key=lambda x: x[1], reverse = True)

for player in sortedCandidates:
    # if the player can be added to the squad then add them to their position and minus their cost of the budget and add 1 to their club count
    if checkValid(player):
        pos = player[0].pos
        cost = player[0].value
        club = player[0].club
        
        budget = budget - cost
        clubCount = count[club]
        count[club] = clubCount + 1

        if pos == "GK":
            GK.append(player)
        elif pos == "DEF":
            DEF.append(player)
        elif pos == "MID":
            MID.append(player)
        else:
            FWD.append(player)
        squad.append(player)

print("\nSQUAD:")
for player in squad:
    print(player[0].name, player[0].pos, player[1])

# fill the starting 11's minimum requirements first
countDEF = countMID = countFWD = 0 # keep count of the positions in the starting XI
startingXI.append(GK[0])
squad.remove(GK[0])
startingXI.append(DEF[0])
startingXI.append(DEF[1]) 
squad.remove(DEF[0])
squad.remove(DEF[1])
countDEF += 2
startingXI.append(MID[0]) 
startingXI.append(MID[1]) 
squad.remove(MID[0])
squad.remove(MID[1])
countMID += 2
startingXI.append(FWD[0])
squad.remove(FWD[0])
countFWD += 1

bench.append(GK[1]) # add the second GK to the bench
squad.remove(GK[1])

# fill the rest of the starting players with the strongest players remaining in the squad, being sure to stick to the formation constraints
for player in squad:
    if len(startingXI) < 11:
        pos = player[0].pos
        if pos == "DEF":
            if countDEF < 5:
                startingXI.append(player)
                countDEF += 1
            else:
                bench.append(player)
        elif pos == "MID":
            if countMID < 5:
                startingXI.append(player)
                countMID += 1
            else:
                bench.append(player)
        else:
            if countFWD < 3:
                startingXI.append(player)
                countFWD += 1
            else:
                bench.append(player)
    else:
        bench.append(player)


print("\nStarting XI:")
for player in startingXI:
    print(player[0].name, player[0].pos, player[1])

print("\nBench:")
for player in bench:
    print(player[0].name, player[0].pos, player[1])