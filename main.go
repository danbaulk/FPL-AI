package main

import (
	"context"
	"database/sql"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"time"

	"cloud.google.com/go/logging"
	db "github.com/danbaulk/FPL-AI/data"
	"github.com/danbaulk/FPL-AI/fpl"
	data "github.com/danbaulk/FPL-AI/handlers/data"
	diagnostics "github.com/danbaulk/FPL-AI/handlers/diagnostics"
	models "github.com/danbaulk/FPL-AI/handlers/models"
	team "github.com/danbaulk/FPL-AI/handlers/team"
	users "github.com/danbaulk/FPL-AI/handlers/users"
	"github.com/danbaulk/FPL-AI/log"
	"github.com/danbaulk/FPL-AI/predictionengine"

	_ "github.com/go-sql-driver/mysql"
)

func main() {
	// Initialise logging
	ctx := context.Background()

	projectID := os.Getenv("PROJECT_ID")
	ctx = log.AddProp(ctx, slog.String("PROJECT_ID:", projectID))
	if projectID != "" {
		cloudClient, err := logging.NewClient(ctx, projectID)
		if err != nil {
			panic(err.Error())
		}
		defer cloudClient.Close()
		log.CloudLogger = cloudClient.Logger("fpl-go-api")
	}

	h := &log.ContextHandler{Handler: slog.NewJSONHandler(os.Stdout, nil)}
	logger := slog.New(h)
	slog.SetDefault(logger)

	// Initialise environment variables
	fpl.SeasonOverviewEndpoint = "https://fantasy.premierleague.com/api/bootstrap-static/"
	fpl.SeasonFixturesEndpoint = "https://fantasy.premierleague.com/api/fixtures/"
	ctx = log.AddProp(ctx, slog.String("FPL_SEASON_OVERVIEW_ENDPOINT", fpl.SeasonOverviewEndpoint))
	ctx = log.AddProp(ctx, slog.String("FPL_SEASON_FIXTURES_ENDPOINT:", fpl.SeasonFixturesEndpoint))

	predictionengine.Host = os.Getenv("ENGINE_HOST")
	ctx = log.AddProp(ctx, slog.String("ENGINE_HOST:", predictionengine.Host))

	db.Username = os.Getenv("MYSQL_USER")
	db.Password = os.Getenv("MYSQL_PASSWORD")
	db.Hostname = os.Getenv("MYSQL_HOST")
	db.Dbname = "fpl"
	ctx = log.AddProp(ctx, slog.String("MYSQL_USER:", db.Username))
	ctx = log.AddProp(ctx, slog.String("MYSQL_PASSWORD:", db.Password))
	ctx = log.AddProp(ctx, slog.String("MYSQL_HOST:", db.Hostname))
	ctx = log.AddProp(ctx, slog.String("MYSQL_DBNAME:", db.Dbname))

	// DB Connection Initialisation
	var err error
	db.Conn, err = sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s)/%s", db.Username, db.Password, db.Hostname, db.Dbname))
	if err != nil {
		log.Critical(ctx, "failed to connect to database", err)
		panic(err.Error())
	}
	db.Conn.SetMaxOpenConns(20)
	db.Conn.SetMaxIdleConns(20)
	db.Conn.SetConnMaxLifetime(time.Minute * 5)
	defer db.Conn.Close()

	log.Info(ctx, "FPL API Initialised")

	// Data endpoints
	http.HandleFunc("/data/gameweekinput", data.GameweekInput)

	// Models endpoints
	http.HandleFunc("/models/predict", models.Predict)

	// Team Management endpoints
	http.HandleFunc("/team/selector", team.Selector)

	// Users endpoints
	http.HandleFunc("/users/", users.Authenticate)

	// Diagnostics endpoints
	http.HandleFunc("/diagnostics/ping", diagnostics.Ping)

	http.ListenAndServe(":8081", nil)

	// TODO: any graceful closing can be deferred
}
