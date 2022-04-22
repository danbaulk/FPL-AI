"""the team selector script will take as input players which want to be included in the team: determined by the 
model to be players who will likely score highly this upcoming gameweek and then output a team which is valid within the FPL 
team creation rules.

It will model the team selection problem as a multi-dinmensional knapsack packing problem (MKP) and aim to opimise it"""

# FPL team rules:
# A squad must be 15 players
# Budget canot exceed 100m
# No more than 3 players from the same club
# A squad consists of 2 GKs, 5 DEFs, 5 MIDs, 3 FWDs
# Starting 11 must have 1 GK, at least 3 DEFs, at least 3 MIDs and at least 1 FWD. No more than 11 players
# Players not in the starting 11 are on the bench and are ordered in terms of substitution priority

import csv
import requests
import json
import Player
from ortools.linear_solver import pywraplp

team_dict = {1: "Arsenal", 2: "Aston Villa", 3: "Brentford", 4: "Brighton", 5: "Burnley", 6: "Chelsea", 7: "Crystal Palace", 8: "Everton", 9: "Leicester", 10: "Leeds", 11: "Liverpool", 12: "Manchester City", 13: "Manchester United", 14: "Newcastle", 15: "Norwich", 16: "Southampton", 17: "Tottenham", 18: "Watford", 19: "West Ham", 20: "Wolves"}

def checkMinReqs(player):
    """pass the function a player to see if they fit in the starting XI without breaking the minimum requirements for a starting XI"""
    valid = True
    pos = player.pos

    # check the positions havent already been filled
    if pos == "GK":
        if len(GK) == 1:
            valid = False
    elif pos == "DEF":
        if len(DEF) == 3:
            valid = False
    elif pos == "MID":
        if len(MID) == 3:
            valid = False
    else:
        if len(FWD) == 1:
            valid = False
    
    # check they arent already added to the team
    for starter in startingXI:
        if starter.name == player.name:
            valid = False

    return valid

def checkFormation(player):
    """pass the function a player to see if they fit in the starting XI without breaking FPL rules"""
    valid = True
    pos = player.pos

    # check starting 11 isnt full
    if len(startingXI) == 11:
        valid = False

    # check the positions havent already been filled
    if pos == "GK":
        if len(GK) == 1:
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
    
    # check they arent already added to the team
    for starter in startingXI:
        if starter.name == player.name:
            valid = False

    return valid

def checkMatch(string1, string2):
    """check that the two given strings match, if so return 1, 0 otherwise"""
    match = 0
    if string1 == string2:
        match = 1
    else:
        match = 0
    return match

def get(url):
    """gets the JSON data from the given URL"""
    response = requests.get(url)
    return json.loads(response.content)

# the input file contains all the players the model predicted would score highly this gameweek along with their confidence
filename = input("Enter the team_candidates file: ")
with open(filename, newline='') as data:
    reader = csv.reader(data)
    candidates = list(reader)
    candidates = candidates[1:] # exclude first row - this is the headings for the data

# a list of player objects in the order theyre given to the MKP solver
players = []

# get the latest data from the FPL API, for example their current price
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
response = get(url)
FPL_players = response['elements']

# get the player data into lists for the MKP solver
data = {}
score = []
cost = []
club = []
position = []

# for each player who is in the candidates list, create a player object for them with their relevant data saved in the object variables
for player in FPL_players:
        currentPlayer = Player.Player()
        currentPlayer.name = player['first_name'] + " " + player['second_name']
        currentPlayer.value = player['now_cost']
        currentPlayer.club = team_dict[player['team']]

        # check if the FPL player is in the candidates list by matching their names
        for candidate in candidates:
            # players with accents occasionally omitted
            if currentPlayer.name == candidate[0]:
                # if the player is a candidate then we store them in the processed candidates list
                currentPlayer.pos = candidate[1]
                confidence = candidate[2]

                score.append(float(confidence))
                cost.append(float(currentPlayer.value))
                club.append(currentPlayer.club)
                position.append(currentPlayer.pos)

                players.append(currentPlayer) # add the player object and to the list of players to retrieve their data later


# get an optimisation solution to the MKP to form a squad using Googles ortools library
solver = pywraplp.Solver.CreateSolver('SCIP')

# add the player data to the data dictionary
data['score'] = score # the return confidence
data['cost'] = cost # the current price of the player
data['club'] = club # the club the player plays for
data['position'] = position # the players position: GK, DEF, MID or FWD
data['players'] = list(range(len(score))) # the number assigned to the player
data['num_players'] = len(score) # the total num of candidates

# add the knapsack constraints to the dictionary
number_bags = 1 # 1 bag for the squad
data['squad_capacity'] = [15]
data['squad'] = list(range(number_bags)) # the number assigned to each bag (just 1 for now)
data['GK_capacity'] = [2]
data['DEF_capacity'] = [5]
data['MID_capacity'] = [5]
data['FWD_capacity'] = [3]
data['budget'] = [1000]
data['club_capacity'] = [3]

# define the constraints of the MKP:
# x[i, b] = 1 if player i is packed in bin b. i.e. 1 if in squad, 0 otherwise
x = {}
for i in data['players']:
    for j in data['squad']:
        x[i, j] = solver.IntVar(0,1,'x_%i_%i' % (i, j))

# each item is assigned to at most one bin. i.e. player is either in the squad or not
for i in data['players']:
    solver.Add(sum(x[i, b] for b in data['squad']) <= 1)

# the total value of the squad cannot exceed 100m
for b in data['squad']:
    solver.Add(sum(x[i, b] * data['cost'][i] for i in data['players']) <= data['budget'][b])

# the squad must consist of exactly 15 players
for b in data['squad']:
    solver.Add(sum(x[i, b] for i in data['players']) == data['squad_capacity'][b])

#  there must be 2 GKs, 5 DEFs, 5 MIDs, 3 FWDs
for b in data['squad']:
     solver.Add(sum(x[i, b] * checkMatch('GK', data['position'][i]) for i in data['players']) == data['GK_capacity'][b])
for b in data['squad']:
     solver.Add(sum(x[i, b] * checkMatch('DEF', data['position'][i]) for i in data['players']) == data['DEF_capacity'][b])
for b in data['squad']:
     solver.Add(sum(x[i, b] * checkMatch('MID', data['position'][i]) for i in data['players']) == data['MID_capacity'][b])
for b in data['squad']:
     solver.Add(sum(x[i, b] * checkMatch('FWD', data['position'][i]) for i in data['players']) == data['FWD_capacity'][b])

# no more than 3 players from any one club
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Arsenal', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Aston Villa', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Brentford', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Brighton', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Burnley', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Chelsea', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Crystal Palace', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Everton', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Leicester', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Leeds', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Liverpool', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Manchester City', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Manchester United', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Newcastle', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Norwich', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Southampton', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Tottenham', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Watford', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('West Ham', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])
for b in data['squad']:
    solver.Add(sum(x[i, b] * checkMatch('Wolves', data['club'][i]) for i in data['players']) <= data['club_capacity'][b])


# Maximize total return confidence of the squad
objective = solver.Objective()
for i in data['players']:
    for b in data['squad']:
        objective.SetCoefficient(x[i, b], data['score'][i])
objective.SetMaximization()

status = solver.Solve()
playerIndex = [] 
squad = [] # 15 man squad

if status == pywraplp.Solver.OPTIMAL:
    for b in data['squad']:
        for i in data['players']:
            if x[i, b].solution_value() == 1:
                # add the player index along with their confidence
                playerIndex.append([i, data['score'][i]])
else:
    print('The problem does not have an optimal solution.')
    # if we reach here it means that it is not possible to field a squad of 15 within the rules

# using the player indexes picked by the MKP solver, match them to their player objects and add them to the squad
for index in playerIndex:
    squad.append([players[index[0]], index[1]]) # add the player object and their confidence to the squad

# with the squad, greedily pick the starting 11 in acordance with the FPL rules
startingXI = [] # the selected starting 11
GK = [] # 2 GK
DEF = [] # 5 DEF
MID = [] # 5 MID
FWD = [] # 3 FWD

# sort the squad in order of confidence
sortedPlayers = sorted(squad, key=lambda x: x[1], reverse = True)
print("\n Squad:")
for player in sortedPlayers:
    print(player[0].name, player[1])

# fill the starting 11's minimum requirements first: 1 GK, 2 DEF, 2 MID, 1 FWD
for player in sortedPlayers:
    # check they can be added to the min reqs starting XI
    if checkMinReqs(player[0]):
        startingXI.append(player[0]) # add the player object to the starting XI
        if player[0].pos == "GK":
            GK.append(player[0])
        elif player[0].pos == "DEF":
            DEF.append(player[0])
        elif player[0].pos == "MID":
            MID.append(player[0])
        else:
            FWD.append(player[0])

# next greedily fill the rest of the starting XI, without breaking the formation rules
for player in sortedPlayers:
    # check they can be added to the min reqs starting XI
    if checkFormation(player[0]):
        startingXI.append(player[0]) # add the player object to the starting XI
        if player[0].pos == "GK":
            GK.append(player[0])
        elif player[0].pos == "DEF":
            DEF.append(player[0])
        elif player[0].pos == "MID":
            MID.append(player[0])
        else:
            FWD.append(player[0])

print("\n Starting XI:")
for player in startingXI:
    print(player.name, player.pos)