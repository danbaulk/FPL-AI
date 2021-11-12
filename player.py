"""
player.py defines player class
"""

class Player:
    def __init__(self, rawData):
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
        self.points = rawData[30] # points earned by player

