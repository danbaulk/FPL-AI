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

func getProps(ctx context.Context) map[string]string {
	props := make(map[string]string)

	if attrs, ok := ctx.Value(slogProps).([]slog.Attr); ok {
		for _, v := range attrs {
			props[v.Key] = v.Value.String()
		}
	}

	return props
}

func addErr(ctx context.Context, err error) context.Context {
	if ctx == nil {
		ctx = context.Background()
	}

	if attrs, ok := ctx.Value(slogProps).([]slog.Attr); ok {
		attrs = append(attrs, slog.String("error_parcel", err.Error()))
		return context.WithValue(ctx, slogProps, attrs)
	}

	attrs := []slog.Attr{}
	attrs = append(attrs, slog.String("error_parcel", err.Error()))
	return context.WithValue(ctx, slogProps, attrs)
}

// AddProp adds a slog attribute to the provided context so that it will be included in any Record created with such context
func AddProp(ctx context.Context, attr slog.Attr) context.Context {
	if ctx == nil {
		ctx = context.Background()
	}

	if attrs, ok := ctx.Value(slogProps).([]slog.Attr); ok {
		attrs = append(attrs, attr)
		return context.WithValue(ctx, slogProps, attrs)
	}

	attrs := []slog.Attr{}
	attrs = append(attrs, attr)
	return context.WithValue(ctx, slogProps, attrs)
}

func Info(ctx context.Context, msg string) {
	slog.InfoContext(ctx, msg)
	if CloudLogger != nil {
		CloudLogger.Log(logging.Entry{
			Severity: logging.Info,
			Payload:  msg,
			Labels:   getProps(ctx),
		})
	}
}

func Error(ctx context.Context, msg string, err error) {
	ctx = addErr(ctx, err)

	slog.ErrorContext(ctx, msg)
	if CloudLogger != nil {
		CloudLogger.Log(logging.Entry{
			Severity: logging.Error,
			Payload:  msg,
			Labels:   getProps(ctx),
		})
	}
}

func Critical(ctx context.Context, msg string, err error) {
	ctx = addErr(ctx, err)

	slog.ErrorContext(ctx, msg)
	if CloudLogger != nil {
		CloudLogger.Log(logging.Entry{
			Severity: logging.Critical,
			Payload:  msg,
			Labels:   getProps(ctx),
		})
	}
}
