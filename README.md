# FPL-AI
AI Based Fantasy Premier League Team Picker

This repository contains tools, models and data for selecting the optimal free-hit team for the upcoming gameweek in FPL.

## Repo Structure

The numbered folders contain retrieved gameweek data, converted to .arff for the Weka models, along with the predictions from the models and the filtered player candidates to be considered for the team. The numbers correspond to the gameweek

The data folder contains the data used for training the machine learning models.

The Models folder contains the machine learning models trained in Weka.

id_dict.csv is a dictionary for looking up player names, understat IDs and FPL IDs.

## Tools
player.py is a class to hold data about player objects.

retrieve_data.py is a tool for retrieving the data for the upcoming gameweek.

team_candidates_generator.py is a tool for creating a list of cnadidates to provide to the team selector, from the results of the models.

team_selector_MKP.py is a tool which takes a team candidates file and solves the multi-dimnesional knapsack packing problem to generate the optimal team within FPL rules.

updateCSV.py is a tool which generates the training data. It combines historical FPL data with historical understat.com data.

## Usage
The training data is already available in the Data folder, as well that machine learning models are already avaialble in the Models folder, so the updateCSV.py tool is one which can be ignored.

1. The first step is to run the retrieve_data.py script, this will output 4 csv files for each position with the players data for the upcoming gameweek. Place this data into a new folder named with the upcoming gameweek and then use Wekas ARFF viewer tool to convert to .arff format and remove the name and pos columns.

2. Then use Weka to make predicictions: load the model you want to use, select the retrieved data as the test set and set output to be a .csv file in the Results folder for the gameweek, then generate the results.

3. Then collate the results into a candidates.csv file and run the the team_candidates_generator.py tool to get the team candidates file. Save these in the Candidates folder of the gameweek folder.

4. Run the team_selector_MKP.py tool with the team candidates file to generate the free-hit squad for the upcoming gameweek.