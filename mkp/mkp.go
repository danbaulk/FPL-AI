package mkp

import "FPL-AI/data"

type Team struct {
	Goalkeeper  []string `json:"goalkeepers"`
	Defenders   []string `json:"defenders"`
	Midfielders []string `json:"midfielders"`
	Forwards    []string `json:"forwards"`
	Subs        []string `json:"subs"`
}

// Solve takes candidates as input and solve the MKP for generating an optimal FPL team within the ruleset
// FPL team rules:
// A squad must be 15 players
// Budget canot exceed 100m
// No more than 3 players from the same club
// A squad consists of 2 GKs, 5 DEFs, 5 MIDs, 3 FWDs
// Starting 11 must have 1 GK, at least 3 DEFs, at least 3 MIDs and at least 1 FWD. No more than 11 players
// Players not in the starting 11 are on the bench and are ordered in terms of substitution priority
func Solve(candidates []data.Candidates) (Team, error) {

	return Team{}, nil
}
