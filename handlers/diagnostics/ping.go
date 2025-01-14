package handlers

import (
	"log/slog"
	"net/http"
	"os"
	"runtime/debug"

	db "github.com/danbaulk/FPL-AI/data"
	"github.com/danbaulk/FPL-AI/log"
	"github.com/danbaulk/FPL-AI/predictionengine"
)

// Ping reports the current running status of the API
func Ping(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	ctx = log.AppendCtx(ctx, slog.String("handler", "ping"))

	// add some debug information to the context
	buildInfo, _ := debug.ReadBuildInfo()
	ctx = log.AppendCtx(ctx, slog.Int("pid", os.Getpid()))
	ctx = log.AppendCtx(ctx, slog.String("go_version", buildInfo.GoVersion))

	// check connection to the JAVA API
	err := predictionengine.Ping()
	if err != nil {
		slog.ErrorContext(ctx, "failed to ping the prediction engine", "error", err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	// check connection to the DB
	err = db.Conn.Ping()
	if err != nil {
		slog.ErrorContext(ctx, "failed to ping the db", "error", err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	slog.InfoContext(ctx, "request processed")
	w.WriteHeader(http.StatusOK)
}
