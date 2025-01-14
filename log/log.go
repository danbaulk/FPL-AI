package log

import (
	"context"
	"fmt"
	"log/slog"
	"os"

	"cloud.google.com/go/logging"
)

type ContextHandler struct {
	slog.Handler
}
type ctxKey string

const (
	slogFields ctxKey = "slog_fields"
)

var (
	ProjectID string

	cloudLogger *logging.Logger
)

// Handle adds contextual attributes to the Record before calling the underlying handler
func (h ContextHandler) Handle(ctx context.Context, r slog.Record) error {
	if attrs, ok := ctx.Value(slogFields).([]slog.Attr); ok {
		for _, v := range attrs {
			r.AddAttrs(v)
		}
	}

	return h.Handler.Handle(ctx, r)
}

// AppendCtx adds an slog attribute to the provided context so that it will be included in any Record created with such context
func AppendCtx(parent context.Context, attr slog.Attr) context.Context {
	if parent == nil {
		parent = context.Background()
	}

	if v, ok := parent.Value(slogFields).([]slog.Attr); ok {
		v = append(v, attr)
		return context.WithValue(parent, slogFields, v)
	}

	v := []slog.Attr{}
	v = append(v, attr)
	return context.WithValue(parent, slogFields, v)
}

func Initialise(ctx context.Context, name string) {
	if ProjectID != "" {
		cloudClient, err := logging.NewClient(ctx, ProjectID)
		if err != nil {
			fmt.Printf("Failed to create client: %v", err)
		}
		defer cloudClient.Close()
		cloudLogger = cloudClient.Logger(name)
	}

	h := &ContextHandler{Handler: slog.NewJSONHandler(os.Stdout, nil)}
	logger := slog.New(h)
	slog.SetDefault(logger)
}

func Info(ctx context.Context, msg string) {
	slog.InfoContext(ctx, msg)
	if cloudLogger != nil {
		cloudLogger.Log(logging.Entry{Severity: logging.Info, Payload: ctx.Value(slogFields)})
	}
}

func Error(ctx context.Context, msg string) {
	slog.ErrorContext(ctx, msg)
	if cloudLogger != nil {
		cloudLogger.Log(logging.Entry{Severity: logging.Error, Payload: ctx.Value(slogFields)})
	}
}
