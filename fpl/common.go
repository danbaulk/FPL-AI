package fpl

type SeasonOverview struct {
	Gameweeks []Gameweek `json:"events"`
	Teams     []Team     `json:"teams"`
	Players   []Player   `json:"elements"`
}

type Gameweek struct {
	ID     int    `json:"id"`
	Name   string `json:"name"`
	IsNext bool   `json:"is_next"`
}

type Team struct {
	ID                  int    `json:"id"`
	Name                string `json:"name"`
	Form                string `json:"form"`
	Strength            int    `json:"strength"`
	OverallStrengthHome int    `json:"strength_overall_home"`
	OverallStrengthAway int    `json:"strength_overall_away"`
	AttackStrengthHome  int    `json:"strength_attack_home"`
	AttackStrengthAway  int    `json:"strength_attack_away"`
	DefenceStrengthHome int    `json:"strength_defence_home"`
	DefenceStrengthAway int    `json:"strength_defence_away"`
}

type Player struct {
	ID           int     `json:"id"`
	Name         string  `json:"web_name"`
	Team         int     `json:"team"`
	Position     int     `json:"element_type"`
	Price        int     `json:"now_cost"`
	Form         string  `json:"form"`
	Influence    string  `json:"influence"`
	Creativity   string  `json:"creativity"`
	Threat       string  `json:"threat"`
	ICTIndex     string  `json:"ict_index"`
	Xg           float64 `json:"expected_goals_per_90"`
	Xa           float64 `json:"expected_assists_per_90"`
	Xgi          float64 `json:"expected_goal_involvements_per_90"`
	Xgc          float64 `json:"expected_goals_conceded_per_90"`
	Availability string  `json:"status"`
}

type Fixture struct {
	ID       int `json:"id"`
	Gameweek int `json:"event"`
	HomeTeam int `json:"team_h"`
	AwayTeam int `json:"team_a"`
}
