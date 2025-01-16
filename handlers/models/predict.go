package handlers

import (
	"log/slog"
	"net/http"

	"github.com/danbaulk/FPL-AI/data"
	"github.com/danbaulk/FPL-AI/log"
	"github.com/danbaulk/FPL-AI/predictionengine"
)

// Predict takes the transformed raw gameweek data and feeds it into the models to generate predictions
// Calls an intermediary Java service which will be running the models to get the predictions
func Predict(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	ctx = log.AddProp(ctx, slog.String("handler", "predict"))

	position := r.FormValue("position")
	gameweek := r.FormValue("gameweek")
	ctx = log.AddProp(ctx, slog.String("position", position))
	ctx = log.AddProp(ctx, slog.String("gameweek", gameweek))

	inputData, err := data.GetInputData(position, gameweek)
	if err != nil {
		log.Error(ctx, "failed to pre process input data", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err.Error()))
		return
	}

	arffData, err := data.ConvertInputToArff(inputData)
	if err != nil {
		log.Error(ctx, "failed to convert input data to arff", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err.Error()))
		return
	}

	predictions, err := predictionengine.Predict(arffData, position)
	if err != nil {
		log.Error(ctx, "prediction engine request failed", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err.Error()))
		return
	}

	err = data.ProcessPredictions(predictions, inputData, gameweek)
	if err != nil {
		log.Error(ctx, "failed to supplement the predictions data", err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err.Error()))
		return
	}

	log.Info(ctx, "request processed")
}
