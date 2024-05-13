package selector

import (
	"errors"
	"sort"

	"github.com/danbaulk/FPL-AI/data"
)

// Squad contains the selected squad
type Squad struct {
	Goalkeepers     []data.Candidate `json:"goalkeepers"`
	Defenders       []data.Candidate `json:"defenders"`
	Midfielders     []data.Candidate `json:"midfielders"`
	Forwards        []data.Candidate `json:"forwards"`
	TotalPrice      int              `json:"price"`
	TotalConfidence float64          `json:"confidence"`
}

// Squad Constraints
const (
	budget            = 1000
	maxPlayers        = 15
	maxGK             = 2
	maxDEF            = 5
	maxMID            = 5
	maxFWD            = 3
	maxPlayersPerClub = 3
)

// Select takes candidates as input and solve the MKP for generating an optimal FPL team within the ruleset
// FPL team rules:
// A squad must be 15 candidates
// Budget canot exceed 100m
// No more than 3 candidates from the same club
// A squad consists of 2 GKs, 5 DEFs, 5 MIDs, 3 FWDs
// Starting 11 must have 1 GK, at least 3 DEFs, at least 3 MIDs and at least 1 FWD. No more than 11 candidates
// Players not in the starting 11 are on the bench and are ordered in terms of substitution priority
func Select(candidates []data.Candidate) (Squad, error) {
	clubCount := map[int]int{}
	squad := Squad{}

	sort.Slice(candidates, func(i, j int) bool {
		return candidates[i].Confidence > candidates[j].Confidence
	})

	for _, candidate := range candidates {
		if clubCount[candidate.Team] >= maxPlayersPerClub {
			continue
		}

		if squad.TotalPrice+candidate.Price > budget {
			continue
		}

		switch candidate.Position {
		case 1:
			if len(squad.Goalkeepers) == maxGK {
				continue
			}
			squad.Goalkeepers = append(squad.Goalkeepers, candidate)
		case 2:
			if len(squad.Defenders) == maxDEF {
				continue
			}
			squad.Defenders = append(squad.Defenders, candidate)
		case 3:
			if len(squad.Midfielders) == maxMID {
				continue
			}
			squad.Midfielders = append(squad.Midfielders, candidate)
		case 4:
			if len(squad.Forwards) == maxFWD {
				continue
			}
			squad.Forwards = append(squad.Forwards, candidate)
		}

		squad.TotalPrice += candidate.Price
		squad.TotalConfidence += candidate.Confidence
		clubCount[candidate.Team]++
	}

	if len(squad.Goalkeepers)+len(squad.Defenders)+len(squad.Midfielders)+len(squad.Forwards) != maxPlayers {
		return Squad{}, errors.New("could not form a valid squad with given constraints")
	}

	return squad, nil
}
