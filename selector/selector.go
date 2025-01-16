package selector

import (
	"math/rand/v2"
	"slices"
	"sort"

	"github.com/danbaulk/FPL-AI/data"
)

// Squad contains the selected squad
type Squad struct {
	Goalkeepers []data.Candidate `json:"goalkeepers"`
	Defenders   []data.Candidate `json:"defenders"`
	Midfielders []data.Candidate `json:"midfielders"`
	Forwards    []data.Candidate `json:"forwards"`
}

// Squad Constraints
const (
	budget            = 1000
	gkSlots           = 2
	defSlots          = 5
	midSlots          = 5
	fwdSlots          = 3
	squadSlots        = 15
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
	squad := Squad{}

	sort.Slice(candidates, func(i, j int) bool {
		return candidates[i].Confidence > candidates[j].Confidence
	})

	budgetCount := budget
	positionCount := map[int]int{1: gkSlots, 2: defSlots, 3: midSlots, 4: fwdSlots}
	clubCount := map[int]int{
		1:  maxPlayersPerClub,
		2:  maxPlayersPerClub,
		3:  maxPlayersPerClub,
		4:  maxPlayersPerClub,
		5:  maxPlayersPerClub,
		6:  maxPlayersPerClub,
		7:  maxPlayersPerClub,
		8:  maxPlayersPerClub,
		9:  maxPlayersPerClub,
		10: maxPlayersPerClub,
		11: maxPlayersPerClub,
		12: maxPlayersPerClub,
		13: maxPlayersPerClub,
		14: maxPlayersPerClub,
		15: maxPlayersPerClub,
		16: maxPlayersPerClub,
		17: maxPlayersPerClub,
		18: maxPlayersPerClub,
		19: maxPlayersPerClub,
		20: maxPlayersPerClub,
	}

	var previousLenCandidates int
	for len(squad.Goalkeepers)+len(squad.Defenders)+len(squad.Midfielders)+len(squad.Forwards) != squadSlots {
		budgetBucket := greedyBudgetPick(candidates, budgetCount)
		positionBucket := greedyPosPick(candidates, positionCount)
		clubBucket := greedyClubPick(candidates, clubCount)

		previousLenCandidates = len(candidates)
		greedyPick(&squad, &candidates, budgetBucket, positionBucket, clubBucket, &budgetCount, &positionCount, &clubCount)

		// if no changes were made to the squad, backtracking is required, so randomly remove a candidate from the squad
		if previousLenCandidates == len(candidates) {
			backtrack(&squad, &budgetCount, &positionCount, &clubCount)
		}
	}

	return squad, nil
}

func backtrack(squad *Squad, budgetCount *int, positionCount, clubCount *map[int]int) {
	randPos := rand.IntN(4) + 1
	var benchWarmer data.Candidate

	switch randPos {
	case 1:
		randIndex := rand.IntN(len(squad.Goalkeepers))
		benchWarmer = squad.Goalkeepers[randIndex]
		squad.Goalkeepers = append(squad.Goalkeepers[:randIndex], squad.Goalkeepers[randIndex+1:]...)
	case 2:
		randIndex := rand.IntN(len(squad.Defenders))
		benchWarmer = squad.Defenders[randIndex]
		squad.Defenders = append(squad.Defenders[:randIndex], squad.Defenders[randIndex+1:]...)
	case 3:
		randIndex := rand.IntN(len(squad.Midfielders))
		benchWarmer = squad.Midfielders[randIndex]
		squad.Midfielders = append(squad.Midfielders[:randIndex], squad.Midfielders[randIndex+1:]...)
	case 4:
		randIndex := rand.IntN(len(squad.Forwards))
		benchWarmer = squad.Forwards[randIndex]
		squad.Forwards = append(squad.Forwards[:randIndex], squad.Forwards[randIndex+1:]...)
	}

	*budgetCount += benchWarmer.Price
	(*positionCount)[benchWarmer.Position]++
	(*clubCount)[benchWarmer.Team]++
}

func greedyPick(squad *Squad, candidates *[]data.Candidate,
	budgetBucket []data.Candidate, positionBucket, clubBucket map[int][]data.Candidate,
	budgetCount *int, positionCount, clubCount *map[int]int) {

	remainingCandidates := []data.Candidate{}

	for _, candidate := range *candidates {
		inBudgetBucket := slices.Contains(budgetBucket, candidate)
		inPositionBucket := slices.Contains(positionBucket[candidate.Position], candidate)
		inClubBucket := slices.Contains(clubBucket[candidate.Team], candidate)

		if inBudgetBucket && inPositionBucket && inClubBucket {
			switch candidate.Position {
			case 1:
				squad.Goalkeepers = append(squad.Goalkeepers, candidate)
			case 2:
				squad.Defenders = append(squad.Defenders, candidate)
			case 3:
				squad.Midfielders = append(squad.Midfielders, candidate)
			case 4:
				squad.Forwards = append(squad.Forwards, candidate)
			}

			*budgetCount -= candidate.Price
			(*positionCount)[candidate.Position]--
			(*clubCount)[candidate.Team]--

			continue
		}

		if inBudgetBucket {
			continue
		}

		remainingCandidates = append(remainingCandidates, candidate)
	}

	*candidates = remainingCandidates
}

func greedyBudgetPick(candidates []data.Candidate, budgetCount int) []data.Candidate {
	budgetBucket := []data.Candidate{}

	for _, candidate := range candidates {
		if budgetCount-candidate.Price > 0 {
			budgetBucket = append(budgetBucket, candidate)
			budgetCount -= candidate.Price
		}
	}

	return budgetBucket
}

func greedyPosPick(candidates []data.Candidate, positionCount map[int]int) map[int][]data.Candidate {
	positionBucket := map[int][]data.Candidate{}
	localCount := make(map[int]int)
	for key, value := range positionCount {
		localCount[key] = value
	}

	for _, candidate := range candidates {
		if localCount[candidate.Position] > 0 {
			positionBucket[candidate.Position] = append(positionBucket[candidate.Position], candidate)
			localCount[candidate.Position]--
		}
	}

	return positionBucket
}

func greedyClubPick(candidates []data.Candidate, clubCount map[int]int) map[int][]data.Candidate {
	clubBucket := map[int][]data.Candidate{}
	localCount := make(map[int]int)
	for key, value := range clubCount {
		localCount[key] = value
	}

	for _, candidate := range candidates {
		if localCount[candidate.Team] > 0 {
			clubBucket[candidate.Team] = append(clubBucket[candidate.Team], candidate)
			localCount[candidate.Team]--
		}
	}

	return clubBucket
}
