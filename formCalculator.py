for row in DataSet:
    currentPlayer = None # current player object
    success = True # whether or not the understat data could be retrieved

    # keep playerDB up to date
    for existingPlayer in player.playerDB:
        if existingPlayer.name == row[2]:
            existingPlayer.update(row) # update the object with new data
            currentPlayer = existingPlayer
            break
    
    # create a player object from the row in the dataset and add it to the playerDB if it doesn't exist in the playerDB
    else:
        player1 = player.Player(row)
        player.playerDB.append(player1) # add the player to the DB
        currentPlayer = player1

    # if the player plays in the game get their understat data
    if (row[17] != "0"):
        loop = asyncio.get_event_loop()
        understatData = loop.run_until_complete(main(currentPlayer.season, currentPlayer.name, currentPlayer.date, currentPlayer.fixture))
        
        # using the current player and row, add the supplemented data to the row
        # only add the data if the understat data could be retrieved
        success = understatData[4]
        if (success):
            currentPlayer.ID = understatData[0]
            currentPlayer.xG = understatData[1]
            currentPlayer.xA = understatData[2]
            currentPlayer.xGC = understatData[3]

            row.extend([currentPlayer.form, currentPlayer.xG, currentPlayer.xA, currentPlayer.xGC, currentPlayer.ID])
            count = count + 1
            print (count)
        else:
            # if the understat data couldnt be retrieved, remove the row
            DataSet.remove(row)