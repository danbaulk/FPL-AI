package handlers

import (
	"fmt"
	"log/slog"
	"net/http"

	"github.com/danbaulk/FPL-AI/fpl"
	"github.com/danbaulk/FPL-AI/log"
)

// NextGameweek proxies a call to the FPL API to get the next gameweek data
func NextGameweek(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	ctx = log.AddProp(ctx, slog.String("handler", "nextgameweek"))

	stats, err := fpl.GetSeasonOverview()
	if err != nil {
		log.Error(ctx, "failed to get season overview stats", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err.Error()))
		return
	}

	var nextGameweek int
	for _, gameweek := range stats.Gameweeks {
		if gameweek.IsNext {
			nextGameweek = gameweek.ID
			break
		}
	}

	log.Info(ctx, "request processed")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Write(fmt.Appendf(nil, "%d", nextGameweek))
}
