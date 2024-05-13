package handlers

import (
	"fmt"
	"net/http"

	"github.com/danbaulk/FPL-AI/data"
	"github.com/danbaulk/FPL-AI/predictionengine"
)

// Predict takes the transformed raw gameweek data and feeds it into the models to generate predictions
// Calls an intermediary Java service which will be running the models to get the predictions
func Predict(w http.ResponseWriter, r *http.Request) {
	position := r.FormValue("position")
	gameweek := r.FormValue("gameweek")

	inputData, err := data.GetInputData(position, gameweek)
	if err != nil {
		err := fmt.Sprintf("message=%q innermessage=%v", "failed to pre process input data", err)
		fmt.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err))
		return
	}

	arffData, err := data.ConvertInputToArff(inputData)
	if err != nil {
		err := fmt.Sprintf("message=%q innermessage=%v", "failed to convert input data to arff", err)
		fmt.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err))
		return
	}

	predictions, err := predictionengine.Predict(arffData, position)
	if err != nil {
		err := fmt.Sprintf("message=%q innermessage=%v", "prediction engine request failed", err)
		fmt.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err))
		return
	}

	err = data.ProcessPredictions(predictions, inputData, gameweek)
	if err != nil {
		err := fmt.Sprintf("message=%q innermessage=%v", "failed to supplement the predictions data", err)
		fmt.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(err))
		return
	}
}
