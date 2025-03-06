# FPL-AI

AI Based Fantasy Premier League Team Picker

This golang backend API provides endpoints for gathering and storing FPL data, using that data to make predictions and using the predictions to select the selecting the optimal free-hit team for the upcoming gameweek in FPL.

## Usage
- Install Docker
- Clone this repo
- cd into the root of this repo
- Build a local image
```bash
docker build -t fpl-ai .
```
- Run the image as a container
```bash
docker run -p 8081:8081 fpl-ai
```
- the /data/nextgameweek endpoint can be used to get the upcoming gameweek ID from the third party
- the /data/gameweekinput endpoint can be used to get the most up to date data from the third party and stores this in the DB
- the /models/predict endpoint can be used to make predictions using the FPL-Predictor for the given gameweek based on the data stored in the DB and will store those predictions in the DB.
- the /team/selector endpoint can be used to select a team for the given gameweek based on the predictions stored in the DB and FPL rules when it comes to creating a valid team
