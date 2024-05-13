package fpl

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

var (
	SeasonOverviewEndpoint string
	SeasonFixturesEndpoint string
)

// GetSeasonOverview makes a request to FPL's API to get the latest gameweeks, teams and players data
func GetSeasonOverview() (SeasonOverview, error) {
	req, err := http.NewRequest(http.MethodGet, SeasonOverviewEndpoint, nil)
	if err != nil {
		return SeasonOverview{}, fmt.Errorf("message=%q error=%v", "failed to create request", err)
	}

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return SeasonOverview{}, fmt.Errorf("message=%q error=%v", "failed to do request", err)
	}

	resBody, err := io.ReadAll(res.Body)
	if err != nil {
		return SeasonOverview{}, fmt.Errorf("message=%q error=%v", "failed to read response body", err)
	}

	var stats SeasonOverview
	err = json.Unmarshal(resBody, &stats)
	if err != nil {
		return SeasonOverview{}, fmt.Errorf("message=%q error=%v", "unable to unmarshal JSON response", err)
	}

	return stats, nil
}

// GetSeasonFixtures makes a request to FPL's API to get the latest fixture data
func GetSeasonFixtures() ([]Fixture, error) {
	req, err := http.NewRequest(http.MethodGet, SeasonFixturesEndpoint, nil)
	if err != nil {
		return []Fixture{}, fmt.Errorf("message=%q error=%v", "failed to create request", err)
	}

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return []Fixture{}, fmt.Errorf("message=%q error=%v", "failed to do request", err)
	}

	resBody, err := io.ReadAll(res.Body)
	if err != nil {
		return []Fixture{}, fmt.Errorf("message=%q error=%v", "failed to read response body", err)
	}

	var fixtures []Fixture
	err = json.Unmarshal(resBody, &fixtures)
	if err != nil {
		return []Fixture{}, fmt.Errorf("message=%q error=%v", "unable to unmarshal JSON response", err)
	}

	return fixtures, nil
}
