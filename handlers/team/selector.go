package handlers

import (
	"encoding/json"
	"log/slog"
	"net/http"

	"github.com/danbaulk/FPL-AI/data"
	"github.com/danbaulk/FPL-AI/log"
	"github.com/danbaulk/FPL-AI/selector"
)

// Selector takes gameweek as an input and generates the optimal free hit squad within the FPL ruleset
// by modelling the team selection problem as a multi-dimensional knapsack packing problem (MKP) and aim to opimise it
func Selector(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	ctx = log.AddProp(ctx, slog.String("handler", "selector"))

	gameweek := r.FormValue("gameweek")
	ctx = log.AddProp(ctx, slog.String("gameweek", gameweek))

	filteredCandidates, err := data.FilterCandidates(gameweek)
	if err != nil {
		log.Error(ctx, "failed to filter the predictions data", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err.Error()))
		return
	}

	selectedTeam, err := selector.Select(filteredCandidates)
	if err != nil {
		log.Error(ctx, "failed to select a team from the given candidates", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err.Error()))
		return
	}

	reponse, err := json.Marshal(selectedTeam)
	if err != nil {
		log.Error(ctx, "failed to marshal JSON response", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err.Error()))
		return
	}

	log.Info(ctx, "request processed")
	w.Write(reponse)
}
