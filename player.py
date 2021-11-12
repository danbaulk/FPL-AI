"""
player.py defines player class
"""
playerDB = [] # maintain a list of player objects

class Player:
    def __init__(self, rawData):
        """constructor for Player"""
        self.season = rawData[1] # season played
        self.gw = rawData[37] # gameweek

        self.name = rawData[2] # name of player
        self.pos = rawData[3] # position of player
        self.value = rawData[34] # value of player

        self.influence = rawData[15] # influence score for player
        self.creativity = rawData[9] # creativity score for player
        self.threat = rawData[29] # threat score for player
        self.ict = rawData[14] # ICT index score for player

        self.fixture = rawData[19] # fixture
        self.wasHome = rawData[35] # was player home or away
        self.points = int(rawData[30]) # points earned by player
        self.performances = [] # list of performances

        self.form = self.calculateForm() # form of player

    def update(self, rawData):
        """Update the player object variables"""
        self.season = rawData[1]
        self.gw = rawData[37]
        self.pos = rawData[3]
        self.value = rawData[34]
        self.influence = rawData[15]
        self.creativity = rawData[9]
        self.threat = rawData[29]
        self.ict = rawData[14]
        self.fixture = rawData[19]
        self.wasHome = rawData[35]
        self.points = int(rawData[30])
        self.form = self.calculateForm()


    def calculateForm(self):
        """calculate recent form of player based on their recent performances"""

        self.performances.append(self.points) # add the points earned to list of performances
        if len(self.performances) > 4:
            self.performances.pop(0) # if performances list is greater than 4 then pop the oldest
        
        form = 0
        for points in self.performances:
            form += points
        form = form / 4
        return form