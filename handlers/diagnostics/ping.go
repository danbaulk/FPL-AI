package handlers

import "net/http"

// Ping reports the current running status of the API
func Ping(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
}
