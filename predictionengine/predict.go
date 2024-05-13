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
	GKEndpoint  string
	DEFEndpoint string
	MIDEndpoint string
	FWDEndpoint string

	ConversionEndpoint string
)

// Predict makes a http request to the prediction engine and returns the response
func Predict(data []byte, position string) ([]byte, error) {
	var endpoint string
	switch position {
	case "1":
		endpoint = GKEndpoint
	case "2":
		endpoint = DEFEndpoint
	case "3":
		endpoint = MIDEndpoint
	case "4":
		endpoint = FWDEndpoint
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

	req, err := http.NewRequest(http.MethodPost, ConversionEndpoint, strings.NewReader(buffer.String()))
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
