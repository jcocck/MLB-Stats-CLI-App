from datetime import datetime
import requests

majorLeagueTeams = [
"Baltimore Orioles", "Boston Red Sox", "New York Yankees", "Tampa Bay Rays", "Toronto Blue Jays", 
    "Chicago White Sox", "Cleveland Guardians", "Detroit Tigers", "Kansas City Royals", "Minnesota Twins", 
    "Houston Astros", "Los Angeles Angels", "Athletics", "Seattle Mariners", "Texas Rangers", 
    "Atlanta Braves", "Miami Marlins", "New York Mets", "Philadelphia Phillies", "Washington Nationals", 
    "Chicago Cubs", "Cincinnati Reds", "Milwaukee Brewers", "Pittsburgh Pirates", "St. Louis Cardinals", 
    "Arizona Diamondbacks", "Colorado Rockies", "Los Angeles Dodgers", "San Diego Padres", "San Francisco Giants"
]

def get_team(mlb, player, name):

    for i in range(30):

        # each team must be checked for the given player

        ids = mlb.get_team_id(majorLeagueTeams[i])
        if ids:
            roster = mlb.get_team_roster(ids[0]) 

            if any(name in str(player) for player in roster):
                return majorLeagueTeams[i]
        else:
            print("Team ID not found.")
    print("DONE")

def check_scores(today): 
    url = "https://statsapi.mlb.com/api/v1/schedule"
    params = {
        "sportId": 1,
        "date": today,
        "hydrate": "team"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Failed to fetch scores.")
        return

    data = response.json()
    dates = data.get("dates", [])

    if not dates:
        print("No games scheduled for today.")
        return

    print("\nHere are the scores for today:\n")
    
    # print the game scores for the day in a readable layout along with the completion status of each.

    for date in dates:
        for game in date.get("games", []):
            teams = game["teams"]

            home = teams["home"]
            away = teams["away"]

            home_team = home["team"]["name"]
            away_team = away["team"]["name"]

            home_score = home.get("score", 0)
            away_score = away.get("score", 0)

            status = game["status"]["abstractGameState"]

            print(
                f"{home_team:<22} {home_score:>2} "
                f"vs {away_team:<22} {away_score:>2}   [{status}]"
            )
            
    
    
    
def normalize_name(name: str) -> str:
    return " ".join(name.lower().split())

# separate get id function that returns an ID given a player name

def get_player_id(player_name: str):
    url = "https://statsapi.mlb.com/api/v1/people/search"
    params = {"names": player_name}

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    target = normalize_name(player_name)
    ids = []

    for person in data["people"]:

        api_name = normalize_name(person.get("firstLastName", ""))

        # Ensure that only exact matches are returned so that incomplete queries don't mistakenly return multiple players
        if api_name == target:
            ids.append(person["id"])
    if ids == []:
        print("\nPlayer not found")
        return
    return ids
    
    
def player_lookup(name):
    
    name = name.title()

    now = datetime.now()

    # get the most recent season by checking if the season for the current year has started or not.
        
    if now < datetime(now.year, 3, 25):
        season = str(now.year - 1)
    else:
        season = str(now.year)
            
    # mapping to streamline the display interface
            
    displayDict = {
        "rbi" : "RBI",
        'team': 'Team',
        'age': 'Age',
        'gamesPlayed': 'Games Played',
        'hits': 'Hits',
        'runs': 'Runs',
        'doubles': 'Doubles',
        'triples': 'Triples',
        'homeRuns': 'Home Runs',
        'strikeOuts': 'Strike Outs',
        'baseOnBalls': 'Base On Balls',
        'atBats': 'At Bats',
        'avg': 'Avg',
        'obp': 'Obp',
        'slg': 'Slg',
        'ops': 'Ops',
        'stolenBases': 'Stolen Bases',
        'caughtStealing': 'Caught Stealing'
    }

    pitcherDisplayDict = {
        'age' : 'Age',
        'numberOfPitches': 'Number Of Pitches',
        'era': 'Era',
        'inningsPitched': 'Innings Pitched',
        'wins': 'Wins',
        'losses': 'Losses',
        'saves': 'Saves',
        'saveOpportunities': 'Save Opportunities',
        'blownSaves': 'Blown Saves',
        'earnedRuns': 'Earned Runs',
        'whip': 'Whip',
        'battersFaced': 'Batters Faced',
        'outs': 'Outs',
        'gamesPitched': 'Games Pitched',
        'strikes': 'Strikes',
        'strikePercentage': 'Strike Percentage',
        'totalBases': 'Total Bases',
        'winPercentage': 'Win Percentage',
        'strikeoutsPer9Inn': 'Strikeouts Per 9 Inn',
        'strikeOuts' : 'Strike Outs'
    }
        # Ensure the player exists
    player_ids = get_player_id(name)
    if not player_ids:
        return
    
    for player_id in player_ids:
    
        pURL = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&season={season}"

        response = requests.get(pURL)
            
        if response.status_code == 200:

            playerData = response.json()
            pos = playerData['stats'][0]['group']['displayName']
            relevantData = playerData['stats'][0]["splits"][0]["stat"]
            teamName = playerData['stats'][0]["splits"][-1]['team']['name'] # use -1 to get the most recent team for up to date info
            for x  in range(3): print() 
                
            # check what kind of data we have to determine which attributes are to be displayed
                
            if  pos == "hitting":
                           
                print(f"Here is the hitting data for {name} of the {teamName} for the {season} season:")
                print("-" * 40)
                for k, v in relevantData.items():
                    if k in displayDict:                    
                        print(f"{displayDict[k]: <22} {v:>10}")
                
            elif pos == "pitching":

                print(f"Here is the pitching data for {name} of the {teamName} for the {season} season:")
                print("-" * 40)
                  
                for k, v in relevantData.items():                
                    if k in pitcherDisplayDict:                   
                        print(f"{pitcherDisplayDict[k]: <22} {v:>10}")

def team_lookup(tName):

    # list of keys that pull pertinent data

    displayKeys = ["teamName", "season", "venue", "abbreviation", "locationName", "active", "league", "division"]

    search_url = "https://statsapi.mlb.com/api/v1/teams?sportId=1"

    # Pull data from all teams
        
    firstResponse = requests.get(search_url)

    if firstResponse.status_code != 200:
        print("Search request failed.")
        return
        
    teams = firstResponse.json().get("teams", [])

    # search for the given team name

    found = False

    done = False

    for team in teams:

        if done == True:
            break

        # Check if the team is in the collection

        if tName.title() in majorLeagueTeams and tName.title() == team['name']:

            found = True

            # make a second request for data specific to tName

            name = tName.title()
            tid = team['id']
            teamURL = f'https://statsapi.mlb.com/api/v1/teams/{tid}'
                
            newResponse = requests.get(teamURL)
            teamInfo = newResponse.json().get("teams",[])

            # now format the output

            leagueName = team['league']['name']
            print("")
            print(f"Now displaying info for the {name} ({leagueName}):\n")
            print("Category            Value","\n")

            for k, v in teamInfo[0].items():
                    
                # only pull data we care about

                if k in displayKeys:
                        
                    # ensure we get the pertinent data should the value be a dict itself

                    if isinstance(v, dict) and 'name' in v:
                        print(f"{k:<20}| {v['name']}")
                    else:
                        print(f"{k:<20}| {v}")       
            done = True

    if found == False:
        print("\nUnable to find a team with that name")   

def main():

    mlb = mlbstatsapi.Mlb()

    # get today's date in YYYY-MM-DD format

    today = datetime.today().strftime('%Y-%m-%d')

    # main control loop that prints a simple CLI menu.

    while True:
        print("\nMLB Stats Menu")
        print("1. Show today's scores")
        print("2. Look up a player")
        print("3. Look up a team")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            check_scores(today)
        elif choice == "2":
            pName = input("Enter name here: ")
            player_lookup(pName)
        elif choice == "3":
            tName = input("Enter name here: ")
            team_lookup(tName)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter 1-4.")

main()
