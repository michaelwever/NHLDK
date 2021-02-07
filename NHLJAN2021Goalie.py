import requests
import csv
import datetime


dateFunction = datetime.datetime.now()

date = (dateFunction.strftime("%Y-%m-%d"))

statsAddress = 'http://statsapi.web.nhl.com/api/v1'
csvFileName = 'NHLDK' + str(date) + '.csv'

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

#def getPlayerRankingData(playerID):
   #return fetchJson(statsAddress + '/people/'+ playerID + '/stats?stats=regularSeasonStatRankings&season')

def getNextOpponentData(teamID):
   return fetchJson(statsAddress + '/teams/' + str(teamID) + '?expand=team.schedule.next')


def getPlayerStats(playerID): 
   data = getPlayerData(playerID)
   #dataranking = getPlayerRankingData(playerID)

   #retrieve next opponent
   teamID = data['people'][0]['currentTeam']['id']
   dataOpponent = getNextOpponentData(teamID)
   opponentName = dataOpponent['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['home']['team']['name']
   opponentID = dataOpponent['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['home']['team']['id']

   #Player Info & Stats
   playerName = data['people'][0]['fullName']
   playerTeam = data['people'][0]['currentTeam']['name']
   position = data['people'][0]['primaryPosition']['type']
   if len(data['people'][0]['stats'][0]['splits'])< 1:
      wins = None
      saves = None
      savePercentage = None
      goalsAgainstAverage = None
      goalsAgainst = None
      gamesStarted = None
   elif position == 'Goalie':
      gamesStarted = data['people'][0]['stats'][0]['splits'][0]['stat']['gamesStarted']
      wins = data['people'][0]['stats'][0]['splits'][0]['stat']['wins']
      saves = data['people'][0]['stats'][0]['splits'][0]['stat']['saves']
      savePercentage = data['people'][0]['stats'][0]['splits'][0]['stat']['savePercentage']
      goalsAgainstAverage = data['people'][0]['stats'][0]['splits'][0]['stat']['goalAgainstAverage']
      goalsAgainst = data['people'][0]['stats'][0]['splits'][0]['stat']['goalsAgainst']
      if gamesStarted == 0:
         gamesStarted = None
      if saves == 0:
         saves = 0.01
   else:
      playerName = None
      wins = None
      saves = None
      savePercentage = None
      goalsAgainstAverage = None
      goalsAgainst = None

   #DK Point Values
   dkbonus = 3
   dkWin = 6
   dkSave = .7
   dkGoalAgainst = -3.5




   #Player Rankings
   #goalsRank = dataranking['stats'][0]['splits'][0]['stat']['rankGoals']



   #retrieves team stats for opponent
   URLOpponent = ('http://statsapi.web.nhl.com/api/v1/teams/' + str(opponentID) + '/?expand=team.stats')
   opponentStats = requests.get(url = URLOpponent)
   VSstats = opponentStats.json()
   #VSGoalsFor = VSstats['teams'][0]['teamStats'][0]['splits'][0]['stat']['goalsPerGame']
   VSGoalsAgainst = VSstats['teams'][0]['teamStats'][0]['splits'][0]['stat']['goalsAgainstPerGame']
   VSShotsAgainst = VSstats['teams'][0]['teamStats'][0]['splits'][0]['stat']['shotsAllowed']
   VSShotsPerGame = VSstats['teams'][0]['teamStats'][0]['splits'][0]['stat']['shotsPerGame']
   VSGoalsPerGame = VSstats['teams'][0]['teamStats'][0]['splits'][0]['stat']['goalsPerGame']
   VSGamesPlayed = VSstats['teams'][0]['teamStats'][0]['splits'][0]['stat']['gamesPlayed']
   VSWins = VSstats['teams'][0]['teamStats'][0]['splits'][0]['stat']['wins']
   VSWinPercentage = VSWins / VSGamesPlayed


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
      
      LeagueGF = LeagueStats['stats'][0]['splits'][0]['stat']['goalsPerGame']
      LeagueGA = LeagueStats['stats'][0]['splits'][0]['stat']['goalsAgainstPerGame']
      LeagueShotsPerGame = LeagueStats['stats'][0]['splits'][0]['stat']['shotsPerGame']
      LeagueShotsAgainstPerGame = LeagueStats['stats'][0]['splits'][0]['stat']['shotsAllowed']
      LeagueSavePercentage = LeagueStats['stats'][0]['splits'][0]['stat']['savePctg']
      TotalLeagueGF = LeagueGF + TotalLeagueGF
      TotalLeagueGA = LeagueGA + TotalLeagueGA
      TotalLeagueShotsPerGame = LeagueShotsPerGame + TotalLeagueShotsPerGame
      TotalLeagueShotsAgainstPerGame = LeagueShotsAgainstPerGame + TotalLeagueShotsAgainstPerGame
      TotalLeagueSavePercentage = LeagueSavePercentage + TotalLeagueSavePercentage
 
      i += 1

   #League Averages
   LeagueGFAverage = TotalLeagueGF/length
   LeagueGAAverage = TotalLeagueGA/length
   LeagueShotsPerGameAverage = TotalLeagueShotsPerGame/length
   LeagueShotsAgainstPerGameAverage = TotalLeagueShotsAgainstPerGame/length
   LeagueSavePercentageAverage = TotalLeagueSavePercentage/length

   #Calculate Player Production Based on Vs Stats
   GoalsAndAssistsMultiplier = VSGoalsAgainst/LeagueGFAverage 
   ShotsAgainstMultiplier = VSShotsAgainst/LeagueShotsAgainstPerGameAverage
   #Stats Per Game
   goalsPerGame = goals/gamesPlayed
   weightedGoalsPerGame = goalsPerGame * GoalsAndAssistsMultiplier
   assistsPerGame = assists/gamesPlayed
   weightedAssistsPerGame = assistsPerGame * GoalsAndAssistsMultiplier
   pointsPerGame = goalsPerGame + assistsPerGame
   weightedPointsPerGame = weightedGoalsPerGame + weightedAssistsPerGame
   shotsPerGame = sog/gamesPlayed
   weightedShotsPerGame = shotsPerGame * ShotsAgainstMultiplier
   blocksPerGame= blocks/gamesPlayed
   shorthandedPointsPerGame = shorthandedPoints/gamesPlayed
   #----------GOALIE CALCULATIONS-----------------------------------------------------
   savesPerGame= saves/gamesStarted
   weightedSavesPerGame= (savesPerGame + VSShotsPerGame) / 2
   weightedGoalsAgainstPerGame= (goalsAgainstAverage + VSGoalsPerGame) / 2
   goalieWinPercentage = wins/gamesStarted
   weightedWinPercentage = (goalieWinPercentage + VSWinPercentage) / 2
   winsPerGame = wins/gamesStarted



   #Calculated DKPoints
   totalDKPoints = 0
   weightedTotalDKPoints = 0
   totalDKPoints = goalsPerGame * dkgoals + assistsPerGame * dkassists + shotsPerGame * dksog + blocksPerGame * dkblock + shorthandedPointsPerGame * dkshorthandedpoint 
   totalDKPointsGoalie = savesPerGame * dkSave + goalsAgainstAverage * dkGoalAgainst + winsPerGame * dkWin
   weightedTotalDKPoints = weightedGoalsPerGame * dkgoals + weightedAssistsPerGame * dkassists + weightedShotsPerGame * dksog + blocksPerGame * dkblock + shorthandedPointsPerGame * dkshorthandedpoint 
   weightedTotalDKPointsGoalie = weightedSavesPerGame * dkSave + weightedGoalsAgainstPerGame * dkGoalAgainst + winsPerGame * weightedWinPercentage
   
   
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
   if weightedWinPercentage > .59:
      weightedTotalDKPoints = weightedTotalDKPoints + 6
   if weightedSavesPerGame > 35:
      weightedTotalDKPoints = weightedTotalDKPoints + dkbonus
   #player stats
   return [playerName, playerTeam, position, round(weightedGoalsPerGame,2), round(weightedAssistsPerGame,2), round(weightedPointsPerGame,2), round(weightedShotsPerGame,2), round(blocksPerGame,2), round(totalDKPoints,2), round(weightedTotalDKPoints,2), round(savesPerGame,2), round(weightedSavesPerGame), round(goalsAgainstAverage,2), round(weightedGoalsAgainstPerGame, 2), round(goalieWinPercentage,2), round(weightedWinPercentage,4), round(totalDKPointsGoalie,2), round(weightedTotalDKPointsGoalie,2)]
# with closes file automatically on exiting block
  

# Request a comma-separated list of team numbers
# convert the entered string to a list of integer values (teams)
#teams = []
#ids = input( "Enter a list of team IDs : " )
#for id in ids.split(","):
 #  teams.append(int(id.strip()))
#print('Preparing stats for the following teams: '+str(teams))

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




# Iterate over the array of team IDs, and display details on each player from each team

# Keep track of how many rows we write into the csvFile
count = 0
with open(csvFileName,'w') as csvFile: # open the file, if it exists overwrite it, if it doesn't create it.
   csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
   csvWriter.writerow(['PlayerName', 'Team', 'Position', 'Weighted Goals', 'Weighted Assists', 'Weighted Points', 'Weighted Shots', 'Blocks', 'Total DK Points', 'Weighted Total DK Points','Saves Per Game', 'Weighted Saves Per Game', 'Goals Against Average', 'Weighted Goals Against Average', 'Win %', 'Weighted Win %', 'Total DK Points Goalie', 'Weighted DK Points Goalie' ])
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




