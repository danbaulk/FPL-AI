package predictionengine

import (
	"bytes"
	"encoding/csv"
	"fmt"
	"io"
	"net/http"
	"strings"
)

var (
	Host string
)

// Predict makes a http request to the prediction engine and returns the response
func Predict(data []byte, position string) ([]byte, error) {
	var endpoint string
	switch position {
	case "1":
		endpoint = Host + "/fplai/predict/gk"
	case "2":
		endpoint = Host + "/fplai/predict/def"
	case "3":
		endpoint = Host + "/fplai/predict/mid"
	case "4":
		endpoint = Host + "/fplai/predict/fwd"
	default:
		return nil, fmt.Errorf("message=%q", "invalid position")
	}

	req, err := http.NewRequest(http.MethodPost, endpoint, bytes.NewReader(data))
	if err != nil {
		return nil, fmt.Errorf("message=%q error=%v", "failed to create request", err)
	}

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("message=%q error=%v", "failed to do request", err)
	}

	resBody, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, fmt.Errorf("message=%q error=%v", "failed to read response body", err)
	}

	return resBody, nil
}

// Convert makes a http request to the prediction engine and returns the response
func Convert(data [][]string) ([]byte, error) {
	var buffer bytes.Buffer
	writer := csv.NewWriter(&buffer)
	err := writer.WriteAll(data)
	if err != nil {
		return nil, fmt.Errorf("message=%q error=%v", "failed to write csv data to buffer", err)
	}
	defer writer.Flush()

	req, err := http.NewRequest(http.MethodPost, Host+"/fplai/data/convert", strings.NewReader(buffer.String()))
	if err != nil {
		return nil, fmt.Errorf("message=%q error=%v", "failed to create request", err)
	}

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("message=%q error=%v", "failed to do request", err)
	}

	resBody, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, fmt.Errorf("message=%q error=%v", "failed to read response body", err)
	}

	return resBody, nil
}
