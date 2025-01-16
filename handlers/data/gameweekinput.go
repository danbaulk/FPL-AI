package handlers

import (
	"log/slog"
	"net/http"

	"github.com/danbaulk/FPL-AI/data"
	"github.com/danbaulk/FPL-AI/fpl"
	"github.com/danbaulk/FPL-AI/log"
)

// GameweekInput fetches the raw gameweek data for the given gameweek and preprocesses it for the models
func GameweekInput(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	ctx = log.AddProp(ctx, slog.String("handler", "gameweekinput"))

	stats, err := fpl.GetSeasonOverview()
	if err != nil {
		log.Error(ctx, "failed to get season overview stats", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err.Error()))
		return
	}

	fixtures, err := fpl.GetSeasonFixtures()
	if err != nil {
		log.Error(ctx, "failed to get season fixture stats", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err.Error()))
		return
	}

	err = data.UpsertLatest(stats, fixtures)
	if err != nil {
		log.Error(ctx, "failed to upsert latest data", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err.Error()))
		return
	}

	log.Info(ctx, "request processed")
}
