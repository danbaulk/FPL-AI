package handlers

import (
	"log/slog"
	"net/http"
	"os"
	"runtime/debug"

	"github.com/danbaulk/FPL-AI/log"
)

// Ping reports the current running status of the API
func Ping(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	ctx = log.AppendCtx(ctx, slog.String("handler", "ping"))

	buildInfo, _ := debug.ReadBuildInfo()
	ctx = log.AppendCtx(ctx, slog.Int("pid", os.Getpid()))
	ctx = log.AppendCtx(ctx, slog.String("go_version", buildInfo.GoVersion))

	slog.InfoContext(ctx, "request processed")
	w.WriteHeader(http.StatusOK)
}
