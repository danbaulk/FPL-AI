package main

import (
	"database/sql"
	"fmt"
	"net/http"
	"time"

	db "FPL-AI/data"
	"FPL-AI/fpl"
	data "FPL-AI/handlers/data"
	diagnostics "FPL-AI/handlers/diagnostics"
	models "FPL-AI/handlers/models"
	team "FPL-AI/handlers/team"
	users "FPL-AI/handlers/users"
	"FPL-AI/predictionengine"

	_ "github.com/go-sql-driver/mysql"
)

func main() {
	// open up connections / initialise services and handlers / initialise environment variables
	// TODO: use flag package

	predictionengine.GKEndpoint = "http://localhost:8080/fplai/predict/gk"
	predictionengine.DEFEndpoint = "http://localhost:8080/fplai/predict/def"
	predictionengine.MIDEndpoint = "http://localhost:8080/fplai/predict/mid"
	predictionengine.FWDEndpoint = "http://localhost:8080/fplai/predict/fwd"
	predictionengine.ConversionEndpoint = "http://localhost:8080/fplai/data/convert"

	fpl.SeasonOverviewEndpoint = "https://fantasy.premierleague.com/api/bootstrap-static/"
	fpl.SeasonFixturesEndpoint = "https://fantasy.premierleague.com/api/fixtures/"

	db.Username = "root"
	db.Password = "root"
	db.Hostname = "127.0.0.1:3306"
	db.Dbname = "fpl"

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

	http.ListenAndServe("localhost:8081", nil)

	// TODO: any graceful closing can be deferred
}
