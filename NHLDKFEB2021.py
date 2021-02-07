import requests
import csv
import datetime

dateFunction = datetime.datetime.now()

date = (dateFunction.strftime("%Y-%m-%d"))

statsAddress = 'http://statsapi.web.nhl.com/api/v1'
csvFileName = 'NHLDK' + str(date) + '.csv'

def getScheduleForToday():
   getTodaysTeams = ('https://statsapi.web.nhl.com/api/v1/schedule?date=' + date)
   getTeams = requests.get(url = getTodaysTeams)
   todaysTeams = getTeams.json()
   numberOfGames = todaysTeams['dates'][0]['totalGames']
   i = 0
   teams = []
   for i in range(0,numberOfGames,1):
    teams.append(todaysTeams['dates'][0]['games'][i]['teams']['away']['team']['id'])
    teams.append(todaysTeams['dates'][0]['games'][i]['teams']['home']['team']['id'])
   print('Preparing stats for the following teams: '+str(teams))

def fetchJson(url):
   response = requests.get(url)
   if response.status_code == 200:
      return response.json()
   else:
      print('Status '+response.status_code+' fetching Json data with '+url)

def getTeamData(teamID):
   return fetchJson(statsAddress + '/teams/' + str(teamID) +'/stats')

def getTeamRosterData(teamID):
   return fetchJson(statsAddress+'/teams/' + str(teamID) + '?expand=team.roster')

def getPlayerData(playerID):
   return fetchJson(statsAddress + '/people/'+ playerID + '?hydrate=stats(splits=statsSingleSeason)')

def OpponentData(teamID):
   return fetchJson(statsAddress + '/teams/' + str(teamID) + '?expand=team.schedule.next')

def getLeagueAverages():
    #retrieves NHL Mean for GF & GA
   LeagueGF = 0  
   LeagueGA = 0
   TotalLeagueGF = 0
   TotalLeagueGA = 0
   TotalLeagueShotsPerGame = 0
   TotalLeagueShotsAgainstPerGame = 0
   TotalLeagueSavePercentage = 0
   teamIDList = [1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,30,52,53,54]
   length = len(teamIDList)
   i = 0
   while i < length:
      LeagueStats = getTeamData(teamIDList[i])
      
      TeamGFAverage = LeagueStats['stats'][0]['splits'][0]['stat']['goalsPerGame']
      TeamGAAverage = LeagueStats['stats'][0]['splits'][0]['stat']['goalsAgainstPerGame']
      TeamShotsPerGame = LeagueStats['stats'][0]['splits'][0]['stat']['shotsPerGame']
      TeamShotsAgainstPerGame = LeagueStats['stats'][0]['splits'][0]['stat']['shotsAllowed']
      TeamSavePercentage = LeagueStats['stats'][0]['splits'][0]['stat']['savePctg']
      TotalLeagueGF = TotalLeagueGF + TeamGFAverage
      TotalLeagueGA = TotalLeagueGA + TeamGAAverage
      TotalLeagueShotsAgainstPerGame = TotalLeagueShotsAgainstPerGame + TeamShotsPerGame 
      i += 1
   #League Averages
   LeagueGFAverage = TotalLeagueGF/31
   LeagueGAAverage = TotalLeagueGA/31
   LeagueShotsPerGameAverage = TotalLeagueShotsPerGame/31
   LeagueShotsAgainstPerGameAverage = TotalLeagueShotsAgainstPerGame/31
   LeagueSavePercentageAverage = TotalLeagueSavePercentage/31
   return[LeagueGAAverage, LeagueShotsAgainstPerGameAverage]

def getPlayerStats(playerID): #Gets Player Stats, returns player info at stats on a per-game basis
    data = getPlayerData(playerID)
    position = data['people'][0]['primaryPosition']['type']
    if len(data['people'][0]['stats'][0]['splits'])< 1:
        playerName = 'N/A'
        position = None
        playerTeam = None
        gamesPlayed = None
        goals = None
        assists = None
        sog = None
        blocks = None
        shorthandedPoints = None
        goalsPerGame = 0
        weightedGoalsPerGame = 0
        assistsPerGame = 0
        weightedAssistsPerGame = 0
        pointsPerGame = 0
        weightedPointsPerGame = 0
        shotsPerGame = 0
        weightedShotsPerGame = 0
        blocksPerGame= 0
        shorthandedPointsPerGame = 0
    elif position == 'Goalie':
            playerName = 'N/A'
            playerTeam = None
            gamesPlayed = None
            goals = None
            assists = None
            sog = None
            blocks = None
            shorthandedPoints = None
            goalsPerGame = 0
            weightedGoalsPerGame = 0
            assistsPerGame = 0
            weightedAssistsPerGame = 0
            pointsPerGame = 0
            weightedPointsPerGame = 0
            shotsPerGame = 0
            weightedShotsPerGame = 0
            blocksPerGame= 0
            shorthandedPointsPerGame = 0
    else:
        playerName = data['people'][0]['fullName']
        playerTeam = data['people'][0]['currentTeam']['name']
        playerTeamID = data['people'][0]['currentTeam']['id']
        gamesPlayed = data['people'][0]['stats'][0]['splits'][0]['stat']['games']
        goals = data['people'][0]['stats'][0]['splits'][0]['stat']['goals']
        assists = data['people'][0]['stats'][0]['splits'][0]['stat']['assists']
        sog = data['people'][0]['stats'][0]['splits'][0]['stat']['shots']
        blocks = data['people'][0]['stats'][0]['splits'][0]['stat']['blocked']
        shorthandedPoints = data['people'][0]['stats'][0]['splits'][0]['stat']['shortHandedPoints']
        goalsPerGame = goals/gamesPlayed
        assistsPerGame = assists/gamesPlayed
        pointsPerGame = goalsPerGame + assistsPerGame
        shotsPerGame = sog/gamesPlayed
        blocksPerGame= blocks/gamesPlayed
        shorthandedPointsPerGame = shorthandedPoints/gamesPlayed
    return [playerName, playerTeam, playerTeamID, goalsPerGame,assistsPerGame,pointsPerGame,shotsPerGame,blocksPerGame,shorthandedPointsPerGame]

def getOppnentStats(LeagueGAAverage,LeagueShotsAgainstPerGameAverage):
   dataOpponent = getNextOpponentData(teamID)
   #opponentName = dataOpponent['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['home']['team']['name']
   opponentID = dataOpponent['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['home']['team']['id']
   #retrieves team stats for opponent
   URLOpponent = ('http://statsapi.web.nhl.com/api/v1/teams/' + str(opponentID) + '/?expand=team.stats')
   opponentStats = requests.get(url = URLOpponent)
   VSstats = opponentStats.json()
   VSGoalsAgainstAverage = VSstats['teams'][0]['teamStats'][0]['splits'][0]['stat']['goalsAgainstPerGame']      
   VSShotsAgainstAverage = VSstats['teams'][0]['teamStats'][0]['splits'][0]['stat']['shotsAllowed']
   GoalsAndAssistsMultiplier = VSGoalsAgainstAverage/LeagueGAAverage 
   ShotsAgainstMultiplier = VSShotsAgainstAverage/LeagueShotsAgainstPerGameAverage
   return[GoalsAndAssistsMultiplier,ShotsAgainstMultiplier]

def weighPlayerStatsVSOpponent():
   weightedGoalsPerGame = goalsPerGame * GoalsAndAssistsMultiplier
   weightedAssistsPerGame = assistsPerGame * GoalsAndAssistsMultiplier
   weightedPointsPerGame = weightedGoalsPerGame + weightedAssistsPerGame
   weightedShotsPerGame = shotsPerGame * ShotsAgainstMultiplier
   return[weightedGoalsPerGame,weightedAssistsPerGame,weightedPointsPerGame,weightedShotsPerGame]

def calculateDKPoints(): #Calculates DL Points & Returns with Player Infomation
   #DK Point Values
   dkgoals = 8.5
   dkassists = 5
   dksog = 1.5
   dkblock = 1.3
   dkshootoutgoal = 1.5
   dkshorthandedpoint = 2
   dkbonus = 3
   totalDKPoints = 0
   weightedTotalDKPoints = 0
   totalDKPoints = goalsPerGame * dkgoals + assistsPerGame * dkassists + shotsPerGame * dksog + blocksPerGame * dkblock + shorthandedPointsPerGame * dkshorthandedpoint 
   weightedTotalDKPoints = weightedGoalsPerGame * dkgoals + weightedAssistsPerGame * dkassists + weightedShotsPerGame * dksog + blocksPerGame * dkblock + shorthandedPointsPerGame * dkshorthandedpoint 
   #Point Bonus
   if pointsPerGame > 2:
      totalDKPoints = totalDKPoints + dkbonus
   if goalsPerGame > 2:
      totalDKPoints = totalDKPoints + dkbonus
   if weightedGoalsPerGame > 2:
      weightedTotalDKPoints = weightedTotalDKPoints + dkbonus
   if blocksPerGame > 2:
      totalDKPoints = totalDKPoints + dkbonus
   if weightedShotsPerGame > 4:
      weightedTotalDKPoints = weightedTotalDKPoints + dkbonus
   if shotsPerGame > 4:
      totalDKPoints = totalDKPoints + dkbonus
   if weightedPointsPerGame > 2:
      weightedTotalDKPoints = weightedTotalDKPoints + dkbonus
   return [playerName, playerTeam, position, round(goalsPerGame,2), round(weightedGoalsPerGame,2), round(assistsPerGame,2), round(weightedAssistsPerGame,2), round(pointsPerGame,2), round(weightedPointsPerGame,2), round(shotsPerGame,2), round(weightedShotsPerGame,2), round(blocksPerGame,2), round(totalDKPoints,2), round(weightedTotalDKPoints,2), round(VSGoalsAgainstAverage,2), round(LeagueGAAverage,2), round(VSShotsAgainstAverage,2), round(LeagueShotsAgainstPerGameAverage,2), round(GoalsAndAssistsMultiplier,2), round(ShotsAgainstMultiplier,2)]

def writeResults():
   count = 0
   with open(csvFileName,'w') as csvFile: # open the file, if it exists overwrite it, if it doesn't create it.
      csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
      csvWriter.writerow(['PlayerName', 'Team', 'Position', 'Goals Per Game','Weighted Goals', 'Assists Per Game','Weighted Assists', 'Points Per Game','Weighted Points', 'Shots Per Game', 'Weighted Shots', 'Blocks', 'Total DK Points', 'Weighted Total DK Points'])
   for teamID in teams:
      teamData = getTeamRosterData(teamID)
   for person in teamData['teams'][0]['roster']['roster']:
      count += 1
      # get the DK points for the current player
      results = getPlayerStats(str(person['person']['id']))
      # add the player data to the csvFile
      csvWriter.writerow(results)
      # display the player data in the console
      print(str(count)+': '+str(results))
   print('Wrote '+str(count)+' player records to '+csvFileName)

getScheduleForToday
fetchJson
getTeamData
getTeamRosterData
OpponentData
getLeagueAverages
getPlayerStats
getOppnentStats
weighPlayerStatsVSOpponent
calculateDKPoints
writeResults