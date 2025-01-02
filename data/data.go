package data

import (
	"encoding/json"
	"fmt"
	"strconv"

	"github.com/danbaulk/FPL-AI/fpl"
	"github.com/danbaulk/FPL-AI/predictionengine"

	"golang.org/x/exp/maps"
)

// UpsertLatest takes the most up to date FPL data and upserts it into the DB
func UpsertLatest(stats fpl.SeasonOverview, fixtures []fpl.Fixture) error {
	for _, gameweek := range stats.Gameweeks {
		err := upsertGameweekData(gameweek)
		if err != nil {
			return fmt.Errorf("message=%q error=%v", "failed to upsert gameweek data", err)
		}
	}

	for _, team := range stats.Teams {
		err := upsertTeamData(team)
		if err != nil {
			return fmt.Errorf("message=%q error=%v", "failed to upsert team data", err)
		}
	}

	for _, player := range stats.Players {
		err := upsertPlayerData(player)
		if err != nil {
			return fmt.Errorf("message=%q error=%v", "failed to upsert player data", err)
		}
	}

	for _, fixture := range fixtures {
		// skip any fixture where gamewek = 0 as this is a fixture TBC and causes a foreign key constraint error
		if fixture.Gameweek == 0 {
			continue
		}

		err := upsertFixtureData(fixture)
		if err != nil {
			return fmt.Errorf("message=%q error=%v", "failed to upsert fixture data", err)
		}
	}

	return nil
}

// GetInputData fetches the relevant FPL data from the DB for making predictions, and preprocesses it for the prediction engine
func GetInputData(position, gameweek string) ([][]string, error) {
	var inputData [][]string
	headers := []string{
		"id",
		"fixture",
		"avg_xG",
		"avg_xA",
		"avg_xGC",
		"avg_I",
		"avg_C",
		"avg_T",
		"avg_ICT",
		"fixture_difficulty",
		"is_home",
		"form",
		"class",
	}
	inputData = append(inputData, headers)

	playersData, err := getPlayers(position)
	if err != nil {
		return nil, fmt.Errorf("message=%q innermessage=%v", "failed to fetch players data", err)
	}

	fixturesData, err := getFixtures(gameweek)
	if err != nil {
		return nil, fmt.Errorf("message=%q innermessage=%v", "failed to fetch fixtures data", err)
	}

	// loop over the available players and the fixtures in the gameweek
	// if the player is playing in a fixture add the details to the inputData slice
	for _, player := range playersData {
		for _, fixture := range fixturesData {
			if (player.Team == fixture.HomeTeam) || (player.Team == fixture.AwayTeam) {
				isHome := 0
				fixtureDifficulty := fixture.HomeTeamStrength
				if player.Team == fixture.HomeTeam {
					isHome = 1
					fixtureDifficulty = fixture.AwayTeamStrength
				}

				details := []string{
					strconv.Itoa(player.ID),
					strconv.Itoa(fixture.FixtureID),
					strconv.FormatFloat(player.Xg, 'f', -1, 64),
					strconv.FormatFloat(player.Xa, 'f', -1, 64),
					strconv.FormatFloat(player.Xgc, 'f', -1, 64),
					player.Influence,
					player.Creativity,
					player.Threat,
					player.ICTIndex,
					strconv.Itoa(fixtureDifficulty),
					strconv.Itoa(isHome),
					player.Form,
					"?"}
				inputData = append(inputData, details)
			}
		}
	}

	return inputData, nil
}

// Prediction is a struct for storing the response from the prediction engine
type Prediction struct {
	PlayerID         string
	Gameweek         string
	FixtureID        string
	Prediction       float64   `json:"predictedClass"`
	ConfidenceScores []float64 `json:"confidenceScores"`
}

// ProcessPredictions supplements the predictions with extra data for storage in the DB
func ProcessPredictions(predictionsData []byte, rawData [][]string, gameweek string) error {
	var predictions []Prediction
	err := json.Unmarshal(predictionsData, &predictions)
	if err != nil {
		return fmt.Errorf("message=%q error=%v", "unable to unmarshal JSON response", err)
	}

	rawData = rawData[1:]
	for i := 0; i < len(predictions); i++ {
		// supplement the predictions with further details
		predictions[i].PlayerID = rawData[i][0]
		predictions[i].Gameweek = gameweek
		predictions[i].FixtureID = rawData[i][1]

		err = upsertPrediction(predictions[i])
		if err != nil {
			return fmt.Errorf("message=%q error=%v", "failed to upsert the predictions to the db", err)
		}
	}

	return nil
}

// FilterCandidates will fetch the  predictions for the given gameweek and filter out any non returners, as well as combine
// doublers / triplers return confidence scores.
func FilterCandidates(gameweek string) ([]Candidate, error) {
	filteredCandidates := map[int]Candidate{}

	candidates, err := getPredictions(gameweek)
	if err != nil {
		return nil, fmt.Errorf("message=%q innermessage=%v", "failed to fetch predictions data", err)
	}

	for _, candidate := range candidates {
		existingCandidate, ok := filteredCandidates[candidate.ID]
		if ok {
			candidate.Confidence += existingCandidate.Confidence
		}
		filteredCandidates[candidate.ID] = candidate
	}

	out := maps.Values(filteredCandidates)

	return out, nil
}

// ConvertInputToArff takes the input data and converts it to ARFF format to be used by the prediction engine
func ConvertInputToArff(rawData [][]string) ([]byte, error) {
	// strip off unnecessary metadata columns for the models
	var inputData [][]string
	for _, row := range rawData {
		inputData = append(inputData, row[2:])
	}

	arffData, err := predictionengine.Convert(inputData)
	if err != nil {
		err := fmt.Errorf("message=%q innermessage=%v", "unable to call conversion endpoint", err)
		return nil, err
	}

	return arffData, nil
}
