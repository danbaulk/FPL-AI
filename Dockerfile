# Build Stage
FROM golang:alpine3.20 AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o /FPL-AI .

# Run Stage
FROM alpine:3.20
COPY --from=builder /FPL-AI /FPL-AI
EXPOSE 8081
CMD ["/FPL-AI"]