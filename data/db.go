package data

import (
	"database/sql"
	"fmt"
	"regexp"
	"strconv"

	"github.com/danbaulk/FPL-AI/fpl"
)

var (
	Username string
	Password string
	Hostname string
	Dbname   string
	Conn     *sql.DB
)

func makeSafe(input string) string {
	re, _ := regexp.Compile(`[^\w]`)
	return re.ReplaceAllString(input, "")
}

func upsertGameweekData(gameweek fpl.Gameweek) error {
	const proc = "upsertGameweekData"

	stmt, err := Conn.Prepare(fmt.Sprintf("CALL %s(%d, '%s', '%s')", proc,
		gameweek.ID,
		gameweek.Name,
		strconv.FormatBool(gameweek.IsNext)))
	if err != nil {
		return err
	}
	defer stmt.Close()

	_, err = stmt.Exec()
	if err != nil {
		return err
	}

	return nil
}

func upsertTeamData(team fpl.Team) error {
	const proc = "upsertTeamData"

	stmt, err := Conn.Prepare(fmt.Sprintf("CALL %s(%d, '%s', '%s', %d, %d, %d, %d, %d, %d, %d)", proc,
		team.ID,
		makeSafe(team.Name),
		team.Form,
		team.Strength,
		team.OverallStrengthHome,
		team.OverallStrengthAway,
		team.AttackStrengthHome,
		team.AttackStrengthAway,
		team.DefenceStrengthHome,
		team.DefenceStrengthAway))
	if err != nil {
		return err
	}
	defer stmt.Close()

	_, err = stmt.Exec()
	if err != nil {
		return err
	}

	return nil
}

func upsertPlayerData(player fpl.Player) error {
	const proc = "upsertPlayerData"

	stmt, err := Conn.Prepare(fmt.Sprintf("CALL %s(%d, '%s', %d, %d, '%s', %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')", proc,
		player.ID,
		makeSafe(player.Name),
		player.Team,
		player.Position,
		player.Availability,
		player.Price,
		player.Form,
		player.Influence,
		player.Creativity,
		player.Threat,
		player.ICTIndex,
		strconv.FormatFloat(player.Xg, 'f', -1, 64),
		strconv.FormatFloat(player.Xa, 'f', -1, 64),
		strconv.FormatFloat(player.Xgi, 'f', -1, 64),
		strconv.FormatFloat(player.Xgc, 'f', -1, 64)))
	if err != nil {
		return err
	}
	defer stmt.Close()

	_, err = stmt.Exec()
	if err != nil {
		return err
	}

	return nil
}

func upsertFixtureData(fixture fpl.Fixture) error {
	const proc = "upsertFixtureData"

	stmt, err := Conn.Prepare(fmt.Sprintf("CALL %s(%d, %d, %d, %d)", proc,
		fixture.ID,
		fixture.Gameweek,
		fixture.HomeTeam,
		fixture.AwayTeam))
	if err != nil {
		return err
	}
	defer stmt.Close()

	_, err = stmt.Exec()
	if err != nil {
		return err
	}

	return nil
}

func upsertPrediction(prediction Prediction) error {
	const proc = "upsertPrediction"

	stmt, err := Conn.Prepare(fmt.Sprintf("CALL %s('%s', '%s', '%s', '%s', '%s', '%s')", proc,
		prediction.PlayerID,
		prediction.Gameweek,
		prediction.FixtureID,
		strconv.FormatFloat(prediction.Prediction, 'f', -1, 64),
		strconv.FormatFloat(prediction.ConfidenceScores[0], 'f', -1, 64),
		strconv.FormatFloat(prediction.ConfidenceScores[1], 'f', -1, 64)))
	if err != nil {
		return err
	}
	defer stmt.Close()

	_, err = stmt.Exec()
	if err != nil {
		return err
	}

	return nil
}

type PlayerInput struct {
	ID         int
	Name       string
	Team       int
	Form       string
	Influence  string
	Creativity string
	Threat     string
	ICTIndex   string
	Xg         float64
	Xa         float64
	Xgi        float64
	Xgc        float64
}

func getPlayers(position string) ([]PlayerInput, error) {
	const proc = "getPlayers"

	stmt, err := Conn.Prepare(fmt.Sprintf("CALL %s('%s')", proc, position))
	if err != nil {
		return []PlayerInput{}, err
	}
	defer stmt.Close()

	res, err := stmt.Query()
	if err != nil {
		return []PlayerInput{}, err
	}
	defer res.Close()

	var results []PlayerInput
	for res.Next() {
		row := PlayerInput{}
		err = res.Scan(
			&row.ID,
			&row.Name,
			&row.Team,
			&row.Form,
			&row.Influence,
			&row.Creativity,
			&row.Threat,
			&row.ICTIndex,
			&row.Xg,
			&row.Xa,
			&row.Xgi,
			&row.Xgc,
		)
		if err != nil {
			return []PlayerInput{}, err
		}
		results = append(results, row)
	}

	return results, nil
}

type FixtureInput struct {
	FixtureID        int
	HomeTeam         int
	HomeTeamStrength int
	AwayTeam         int
	AwayTeamStrength int
}

func getFixtures(gameweek string) ([]FixtureInput, error) {
	const proc = "getFixtures"

	stmt, err := Conn.Prepare(fmt.Sprintf("CALL %s('%s')", proc, gameweek))
	if err != nil {
		return []FixtureInput{}, err
	}
	defer stmt.Close()

	res, err := stmt.Query()
	if err != nil {
		return []FixtureInput{}, err
	}
	defer res.Close()

	var results []FixtureInput
	for res.Next() {
		row := FixtureInput{}
		err = res.Scan(
			&row.FixtureID,
			&row.HomeTeam,
			&row.HomeTeamStrength,
			&row.AwayTeam,
			&row.AwayTeamStrength,
		)
		if err != nil {
			return []FixtureInput{}, err
		}
		results = append(results, row)
	}

	return results, nil
}

type Candidate struct {
	ID         int
	Name       string
	Team       int
	Position   int
	Price      int
	Confidence float64
}

func getPredictions(gameweek string) ([]Candidate, error) {
	const proc = "getPredictions"

	stmt, err := Conn.Prepare(fmt.Sprintf("CALL %s('%s')", proc, gameweek))
	if err != nil {
		return []Candidate{}, err
	}
	defer stmt.Close()

	res, err := stmt.Query()
	if err != nil {
		return []Candidate{}, err
	}
	defer res.Close()

	var results []Candidate
	for res.Next() {
		row := Candidate{}
		err = res.Scan(
			&row.ID,
			&row.Name,
			&row.Team,
			&row.Position,
			&row.Price,
			&row.Confidence,
		)
		if err != nil {
			return []Candidate{}, err
		}
		results = append(results, row)
	}

	return results, nil
}
