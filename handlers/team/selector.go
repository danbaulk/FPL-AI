package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/danbaulk/FPL-AI/data"
	"github.com/danbaulk/FPL-AI/selector"
)

// Selector takes gameweek as an input and generates the optimal free hit squad within the FPL ruleset
// by modelling the team selection problem as a multi-dinmensional knapsack packing problem (MKP) and aim to opimise it
func Selector(w http.ResponseWriter, r *http.Request) {
	gameweek := r.FormValue("gameweek")

	filteredCandidates, err := data.FilterCandidates(gameweek)
	if err != nil {
		err := fmt.Sprintf("message=%q innermessage=%v", "failed to filter the predictions data", err)
		fmt.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err))
		return
	}

	selectedTeam, err := selector.Select(filteredCandidates)
	if err != nil {
		err := fmt.Sprintf("message=%q innermessage=%v", "failed to select a team from the given candidates", err)
		fmt.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err))
		return
	}

	reponse, err := json.Marshal(selectedTeam)
	if err != nil {
		err := fmt.Sprintf("message=%q innermessage=%v", "failed to marshal JSON response", err)
		fmt.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err))
		return
	}

	w.Write(reponse)
}
