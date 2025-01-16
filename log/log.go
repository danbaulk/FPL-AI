package log

import (
	"context"
	"log/slog"

	"cloud.google.com/go/logging"
)

type ContextHandler struct {
	slog.Handler
}

type ctxKey string

const slogProps ctxKey = "slog-props"

var (
	CloudLogger *logging.Logger
)

// Handle adds contextual attributes to the Record before calling the underlying handler
func (h ContextHandler) Handle(ctx context.Context, r slog.Record) error {
	if attrs, ok := ctx.Value(slogProps).([]slog.Attr); ok {
		for _, v := range attrs {
			r.AddAttrs(v)
		}
	}

	return h.Handler.Handle(ctx, r)
}

// AddProp adds a slog attribute to the provided context so that it will be included in any Record created with such context
func AddProp(parent context.Context, attr slog.Attr) context.Context {
	if parent == nil {
		parent = context.Background()
	}

	if v, ok := parent.Value(slogProps).([]slog.Attr); ok {
		v = append(v, attr)
		return context.WithValue(parent, slogProps, v)
	}

	v := []slog.Attr{}
	v = append(v, attr)
	return context.WithValue(parent, slogProps, v)
}

func Info(ctx context.Context, msg string) {
	slog.InfoContext(ctx, msg)
	if CloudLogger != nil {
		CloudLogger.Log(logging.Entry{
			Severity: logging.Info,
			Payload:  msg,
			Labels:   ctx.Value(slogProps).(map[string]string),
		})
	}
}

func Error(ctx context.Context, msg string) {
	slog.ErrorContext(ctx, msg)
	if CloudLogger != nil {
		CloudLogger.Log(logging.Entry{
			Severity: logging.Error,
			Payload:  msg,
			Labels:   ctx.Value(slogProps).(map[string]string),
		})
	}
}
