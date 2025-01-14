package main

import (
	"context"
	"database/sql"
	"fmt"
	"net/http"
	"os"
	"time"

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
	log.ProjectID = os.Getenv("PROJECT_ID")
	fmt.Println("PROJECT_ID:", log.ProjectID)
	log.Initialise(ctx, "fpl-go-api")

	// Initialise environment variables
	fpl.SeasonOverviewEndpoint = "https://fantasy.premierleague.com/api/bootstrap-static/"
	fpl.SeasonFixturesEndpoint = "https://fantasy.premierleague.com/api/fixtures/"
	fmt.Println("FPL_SEASON_OVERVIEW_ENDPOINT:", fpl.SeasonOverviewEndpoint)
	fmt.Println("FPL_SEASON_FIXTURES_ENDPOINT:", fpl.SeasonFixturesEndpoint)

	predictionengine.Host = os.Getenv("ENGINE_HOST")
	fmt.Println("ENGINE_HOST:", predictionengine.Host)

	db.Username = os.Getenv("MYSQL_USER")
	db.Password = os.Getenv("MYSQL_PASSWORD")
	db.Hostname = os.Getenv("MYSQL_HOST")
	db.Dbname = "fpl"
	fmt.Println("MYSQL_USER:", db.Username)
	fmt.Println("MYSQL_PASSWORD:", db.Password)
	fmt.Println("MYSQL_HOST:", db.Hostname)
	fmt.Println("MYSQL_DBNAME:", db.Dbname)

	// DB Connection Initialisation
	var err error
	db.Conn, err = sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s)/%s", db.Username, db.Password, db.Hostname, db.Dbname))
	if err != nil {
		panic(err.Error())
	}
	db.Conn.SetMaxOpenConns(20)
	db.Conn.SetMaxIdleConns(20)
	db.Conn.SetConnMaxLifetime(time.Minute * 5)
	defer db.Conn.Close()

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
