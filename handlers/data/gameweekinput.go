package handlers

import (
	"fmt"
	"net/http"

	"github.com/danbaulk/FPL-AI/data"
	"github.com/danbaulk/FPL-AI/fpl"
)

// GameweekInput fetches the raw gameweek data for the given gameweek and preprocesses it for the models
func GameweekInput(w http.ResponseWriter, r *http.Request) {
	stats, err := fpl.GetSeasonOverview()
	if err != nil {
		err := fmt.Sprintf("message=%q innermessage=%v", "failed to get season overview stats", err)
		fmt.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err))
		return
	}

	fixtures, err := fpl.GetSeasonFixtures()
	if err != nil {
		err := fmt.Sprintf("message=%q innermessage=%v", "failed to get season fixture stats", err)
		fmt.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err))
		return
	}

	err = data.UpsertLatest(stats, fixtures)
	if err != nil {
		err := fmt.Sprintf("message=%q innermessage=%v", "failed to upsert latest data", err)
		fmt.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err))
		return
	}
}
