"""
Player.py defines player class, uses the formatting provided by merged_cleaned_seasons.csv in Vaastavs Git repo
"""
playerDB = [] # maintain a list of player objects

def addRecentStats(statsList, stat):
    """add the recent stats of the player to their stats list and cap it at 4"""
    statsList.append(stat) # add the points earned to list of performances
    if len(statsList) > 4:
        statsList.pop(0) # if performances list is greater than 4 then pop the oldest
    return statsList

def calcAvg(statsList):
    """calculate the average of the recent stats list"""
    avg = 0
    if len(statsList) > 0:
        for stat in statsList:
            avg += stat
        avg = avg / len(statsList) # calculate as an average of the max 4 most recent performances
    return avg

class Player:
    def __init__(self, *rawData):
        """constructor for Player
        pass no args, then a default player object is created
        pass raw data, then the object is initalised with that data"""

        if len(rawData) == 1:
            # initialise an object using the raw data passed to the constructor
            self.season = rawData[1][:4] # season played (first 4 letters of the string)
            self.gw = rawData[37] # gameweek
            self.date = rawData[16][:-1].split("T") # date and time of the game - reformatted

            self.ID = 0 # FPL ID
            self.name = rawData[2] # name of player
            self.pos = rawData[3] # position of player
            self.value = rawData[34] # value of player
            self.club = "My Team" # the club of the player

            # recent stats lists for the player (max 4)
            self.influence = [float(rawData[15])] # influence score for player
            self.creativity = [float(rawData[9])] # creativity score for player
            self.threat = [float(rawData[29])] # threat score for player
            self.ict = [float(rawData[14])] # ICT index score for player
            self.xG = [0] # expected Goals
            self.xA = [0] # expected Assists
            self.xGC = [0] # expected Goals Conceded (for players team in that match)

            self.fixture = rawData[19] # fixture difficulty
            self.wasHome = rawData[35] # was player home or away
            self.points = int(rawData[30]) # points earned by player
            self.performances = [int(rawData[30])] # list of recent performances (max 4)

            # the average stats of a player
            self.form = self.avg_xG = self.avg_xA = self.avg_xGC = self.avg_I = self.avg_C = self.avg_T = self.avg_ICT = 0

        else:
            # initialise a blank object if no arguements are passed to constructor
            self.season = "" 
            self.gw = "" 
            self.date = "" 
            self.ID = 0
            self.name = ""
            self.pos = ""
            self.value = ""
            self.club = ""
            self.influence = []
            self.creativity = []
            self.threat = []
            self.ict = []
            self.xG = []
            self.xA = []
            self.xGC = []
            self.fixture = ""
            self.wasHome = ""
            self.points = 0
            self.performances = []
            self.form = self.avg_xG = self.avg_xA = self.avg_xGC = self.avg_I = self.avg_C = self.avg_T = self.avg_ICT = 0
            
    
    def update(self, rawData):
        """update the player object variables"""
        self.season = rawData[1][:4]
        self.gw = rawData[37]
        self.date = rawData[16][:-1].split("T")
        self.pos = rawData[3]
        self.value = rawData[34]
        self.influence = addRecentStats(self.influence, float(rawData[15]))
        self.creativity = addRecentStats(self.creativity, float(rawData[9]))
        self.threat = addRecentStats(self.threat, float(rawData[29]))
        self.ict = addRecentStats(self.ict, float(rawData[14]))
        self.performances = addRecentStats(self.performances, int(rawData[30]))
        self.fixture = rawData[19]
        self.wasHome = rawData[35]
        self.points = int(rawData[30])

    def updateAvgs(self):
        """update the avgs for when the understat data has been added"""
        self.form = calcAvg(self.performances)
        self.avg_xG = calcAvg(self.xG)
        self.avg_xA = calcAvg(self.xA)
        self.avg_xGC = calcAvg(self.xGC)
        self.avg_I = calcAvg(self.influence)
        self.avg_C = calcAvg(self.creativity)
        self.avg_T = calcAvg(self.threat) 
        self.avg_ICT = calcAvg(self.ict)