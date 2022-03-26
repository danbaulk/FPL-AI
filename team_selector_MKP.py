"""the team selector script will take as input players which want to be included in the team: determined by the 
model to be players who will likely score highly this upcoming gameweek and then output a team which is valid within the FPL 
team creation rules.

It will modelthe team selection problem as a multi-dinmensional knapsack packing problem (MKP) and aim to opimise it"""

# FPL team rules:
# A squad must be 15 players
# Budget canot exceed 100m
# No more than 3 players from the same club
# A squad consists of 2 GKs, 5 DEFs, 5 MIDs, 3 FWDs
# Starting 11 must have 1 GK, at least 2 DEFs, at least 2 MIDs and at least 1 FWD. No more than 11 players
# Players not in the starting 11 are on the bench and are ordered in terms of substitution priority

import csv
import requests
import json
import Player
import ortools
from ortools.linear_solver import pywraplp

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
filename = input("Enter the team_candidates file: ")
with open(filename, newline='') as data:
    reader = csv.reader(data)
    candidates = list(reader)
    candidates = candidates[1:] # exclude first row - this is the headings for the data

# a list of player objects and their asociated confidence of scoring highly
processedCandidates = []

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
            if currentPlayer.name == candidate[0]:
                # if the player is a candidate then we store them in the processed candidates list
                currentPlayer.pos = candidate[1]
                confidence = candidate[2]

                score.append(float(confidence))
                cost.append(float(currentPlayer.value))
                club.append(currentPlayer.club)
                position.append(currentPlayer.pos)

                processedCandidates.append([currentPlayer, confidence]) # add the player object and their confidence score to the list


# sort the processed candidates list by their confidence
sortedCandidates = sorted(processedCandidates, key=lambda x: x[1], reverse = True)

# get an optimisation solution to the MKP to form a squad
solver = solver = pywraplp.Solver.CreateSolver('SCIP')

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

# #  there must be 2 GKs, 5 DEFs, 5 MIDs, 3 FWDs
# for b in data['squad']:
#      solver.Add(sum(x[i, b] * list(data['position'][i]).count('GK') for i in data['players']) == data['GK_capacity'][b])
# for b in data['squad']:
#      solver.Add(sum(x[i, b] * list(data['position'][i]).count('DEF') for i in data['players']) == data['DEF_capacity'][b])
# for b in data['squad']:
#      solver.Add(sum(x[i, b] * list(data['position'][i]).count('MID') for i in data['players']) == data['MID_capacity'][b])
# for b in data['squad']:
#      solver.Add(sum(x[i, b] * list(data['position'][i]).count('FWD') for i in data['players']) == data['FWD_capacity'][b])

# # no more than 3 players from any one club
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Arsenal') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Aston Villa') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Brentford') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Brighton') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Burnley') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Chelsea') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Crystal Palace') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Everton') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Leicester') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Leeds') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Liverpool') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Manchester City') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Manchester United') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Newcastle') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Norwich') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Southampton') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Tottenham') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Watford') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('West Ham') for i in data['players']) == data['club_capacity'][b])
# for b in data['squad']:
#     solver.Add(sum(x[i, b] * list(data['club'][i]).count('Wolves') for i in data['players']) == data['club_capacity'][b])


# Maximize total return confidence of the squad
objective = solver.Objective()
for i in data['players']:
    for b in data['squad']:
        objective.SetCoefficient(x[i, b], data['score'][i])
objective.SetMaximization()

status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print(f'Total squad confidence: {objective.Value()}')
    for b in data['squad']:
        print(f'Squad {b}')
        for i in data['players']:
            if x[i, b].solution_value() == 1:
                print(f"Player {i} Cost: {data['cost'][i]} Confidence: {data['score'][i]}")
else:
    print('The problem does not have an optimal solution.')

# with the squad greedily pick the starting 11 in acordance with the FPL rules