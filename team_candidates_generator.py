"""the team candidates generator script will take as input a combined file of all the retrieved data for each position and each of the predictions
made by the models. It will then remove all the non returners and handle any possible doubles or triples.

In order to create the input file, simply combine the retrieved data files, and append to it each of the predictions made by the models, you
should then remove the unnecessary columns and have only name, position, predicted and prediction.

The outputted file will be the team candidates which can be used by the team selector."""
import csv

candidates_file = input("Input the candidates file: ")
# read data from the specifed file into a list called candidates
with open(candidates_file, newline='') as Data:
    reader = csv.reader(Data)
    DataSet = list(reader)
    candidates = DataSet[1:] # exclude first row - this is the headings for the data

# remove all the players who are predicted a no return
returners = []
for player in candidates:
    if player[2] == "2:return":
        player.pop(2) # remove the prediction column as it is no longer needed
        returners.append(player)

# check if there are any doublers in the returners list
names = []
doublers = []
for player in returners:
    for name in names:
        if player[0] == name:
            doublers.append(player[0])
        else:
            names.append(player[0])

# with the list of doublers names sum their return confidences and remove the duplicates
for doubler in doublers:
    newConfidence = 0
    for player in returners:
        if player[0] == doubler[0]:
            newConfidence += player[2]
    returners = [x for x in returners if not x[0] == doubler[0]] # create the new returners list with the doubler removed
    returners.append([doubler[0], doubler[1], newConfidence]) # add the new entry to the returners list

# write the returners to the team candidates file
upcomingGW = input("What is the upcoming gameweek: ")
with open('team_candidates_' + upcomingGW + '.csv', 'w', encoding="utf-8", newline='') as f:
    writer = csv.writer(f)
    header = ['name', 'pos', 'return_confidence']
    writer.writerow(header)
    for row in returners:
        writer.writerow(row)