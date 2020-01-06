from flask import Flask, jsonify, abort, request
import pandas as pd
import numpy as np
import time

app = Flask(__name__)


# sample code for loading the team_info.csv file into a Pandas data frame.  Repeat as
# necessary for other files
def load_teams_data():
    td = pd.read_csv("./team_info.csv")
    return td
def load_game_data():
    td = pd.read_csv("./game.csv")
    return td
def load_player_info():
    td = pd.read_csv("./player_info.csv")
    return td
def load_game_skater_stats():
    td = pd.read_csv("./game_skater_stats.csv")
    return td
def load_game_teams_stats():
    td = pd.read_csv("./game_teams_stats.csv")
    return td
def load_game_plays():
	td = pd.read_csv("./game_plays.csv")
	return td
def load_game_plays_players():
	td = pd.read_csv("./game_plays_players.csv")
	return td


#global variables
team_data = load_teams_data()
print("successfully loaded teams data")
game_data = load_game_data()
print("successfully loaded games data")
player_info = load_player_info()
print("successfully loaded player info data")
game_skater_stats = load_game_skater_stats()
print("successfully loaded game skater stats data")
game_team_stats = load_game_teams_stats()
print("successfully loaded game team stats data")

game_plays_data = load_game_plays()
print("successfully loaded game plays data")
game_plays_players_data = load_game_plays_players()
print("successfully loaded game plays players data")



@app.route('/')
def index():
    return "NHL API"


# route mapping for HTTP GET on /api/schedule/TOR
@app.route('/api/teams/<string:team_id>', methods=['GET'])
def get_task(team_id):
    # fetch sub dataframe for all teams (hopefully 1) where abbreviation=team_id
    teams = team_data[team_data["abbreviation"] == team_id]

    # return 404 if there isn't one team
    if teams.shape[0] < 1:
        abort(404)

    # get first team
    team = teams.iloc[0]

    # return customized JSON structure in lieu of Pandas Dataframe to_json method
    teamJSON = {"abbreviation": team["abbreviation"],
                "city": team["shortName"],
                "name": team["teamName"]}

    # jsonify easly converts maps to JSON strings
    return jsonify(teamJSON)

@app.route('/api/results', methods=['GET'])
def get_results_summary():
    date_str = request.args.get('date')
    gameJSON = {}

    games = game_data[game_data["date_time"] == date_str]

    if games.shape[0] < 1:
        abort(404)


    i = 0

    while i < len(games.index):
        game = games.iloc[i]

        home_team_name = team_data[team_data["team_id"] == game["home_team_id"]].iloc[0]["teamName"]
        away_team_name = team_data[team_data["team_id"] == game["away_team_id"]].iloc[0]["teamName"]
        outcome = outcome_simplifier(game["outcome"])

        gameJSON[int(game["game_id"])] = {
                        "home_team": home_team_name,
                        "away_team": away_team_name,
                        "home_goals": int(game["home_goals"]),
                        "away_goals": int(game["away_goals"]),
                        "outcome": outcome
                    }
        i += 1

    return jsonify(gameJSON)

@app.route('/api/results/<int:game_id>/teams', methods=['GET'])
def get_game_result_details(game_id):

    game = game_team_stats[game_team_stats["game_id"] == game_id]
    if game.shape[0] < 1:
        abort(404)

    team1 = game.iloc[0]
    team2 = game.iloc[1]

    team_1_full_name = (team_data[team_data["team_id"] == team1["team_id"]]).iloc[0]["teamName"]
    team_2_full_name = (team_data[team_data["team_id"] == team2["team_id"]]).iloc[0]["teamName"]


    teamJSON = {
                team_1_full_name: {
                    "Goals": int(team1["goals"]),
                    "Shots": int(team1["shots"]),
                    "Hits": int(team1["hits"]),
                    "PIM": int(team1["pim"]),
                    "PowerPlay Opportunities": int(team1["powerPlayOpportunities"]),
                    "PowerPlay Goals": int(team1["powerPlayGoals"]),
                    "Faceoff Win %": float(team1["faceOffWinPercentage"]),
                    "Giveaways": int(team1["giveaways"]),
                    "takeaways": int(team1["takeaways"])
                },
                team_2_full_name: {
                    "Goals": int(team2["goals"]),
                    "Shots": int(team2["shots"]),
                    "Hits": int(team2["hits"]),
                    "PIM": int(team2["pim"]),
                    "PowerPlay Opportunities": int(team2["powerPlayOpportunities"]),
                    "PowerPlay Goals": int(team2["powerPlayGoals"]),
                    "Faceoff Win %": float(team2["faceOffWinPercentage"]),
                    "Giveaways": int(team2["giveaways"]),
                    "takeaways": int(team2["takeaways"])

                }
                }

    return jsonify(teamJSON)

@app.route('/api/results/<int:game_id>/players', methods=['GET'])
def get_game_player_stats(game_id):

    game_players = game_skater_stats[game_skater_stats["game_id"] == game_id]

    if game_players.shape[0] < 1:
        abort(404)
    team1_id = game_players.iloc[0]["team_id"]
    team2_id = 0

    for i in range(1, game_players.shape[0]):
        if game_players.iloc[i]["team_id"] != team1_id:
            team2_id = game_players.iloc[i]["team_id"]
            break

    team1_full_name = team_data[team_data["team_id"] == team1_id].iloc[0]["teamName"]
    team2_full_name = team_data[team_data["team_id"] == team2_id].iloc[0]["teamName"]

    playersJSON = {
                team1_full_name: {
                    },
                team2_full_name: {
                    }
                }

    for i in range(game_players.shape[0]):
        playerFirstName = player_info[game_players.iloc[i]["player_id"] == player_info["player_id"]].iloc[0]["firstName"]
        playerLastName = player_info[game_players.iloc[i]["player_id"] == player_info["player_id"]].iloc[0]["lastName"]
        playerLastName = ' ' + playerLastName

        playerStats = {
                "G": int(game_players.iloc[i]["goals"]),
                "A": int(game_players.iloc[i]["assists"]),
                "S": int(game_players.iloc[i]["goals"]),
                "H": int(game_players.iloc[i]["hits"]),
                "PPP": int(game_players.iloc[i]["powerPlayGoals"] + game_players.iloc[i]["powerPlayAssists"]),
                "PIM": int(game_players.iloc[i]["penaltyMinutes"]),
                "TkA": int(game_players.iloc[i]["takeaways"]),
                "GvA": int(game_players.iloc[i]["giveaways"]),
                "BkS": int(game_players.iloc[i]["blocked"]),
                "+/-": int(game_players.iloc[i]["plusMinus"]),
        }

        if game_players.iloc[i]["team_id"] == team1_id:
            playersJSON[team1_full_name][playerFirstName + playerLastName] = playerStats
        else:
            playersJSON[team2_full_name][playerFirstName + playerLastName] = playerStats

    return jsonify(playersJSON)

# #Enhancements
@app.route('/api/results/<int:game_id>/scoringsummary', methods=['GET'])
def get_scoring_summary(game_id):
	sorted_plays = game_plays_data.sort_values(by=['period', 'periodTime'])
	plays = sorted_plays[game_plays_data["game_id"] == game_id]
	game = game_data[game_data["game_id"] == game_id]
	playsJSON = {}
	period_dict = {1: "1st Period", 2: "2nd Period", 3: "3rd Period", 4: "4th Period"}

	if plays.shape[0] < 1:
		abort(404)

	periods_in_game = plays.iloc[plays.shape[0] - 1]['period']
	# print(per)

	period = 1

	while period <= periods_in_game:
		playsJSON[period_dict[period]] = {}
		period += 1

	period = 1

	while period <= periods_in_game:
		for i in range(plays.shape[0]):
			if int(plays.iloc[i]["period"]) == period and plays.iloc[i]["event"] == "Goal":
				goal_info = find_goal_info(plays.iloc[i]["play_id"])
				period_time = time.strftime('%M:%S', time.gmtime(int(plays.iloc[i]["periodTime"])))

				desc_list = plays.iloc[i]["description"].split()
				record = player_record(desc_list)

				playsJSON[period_dict[period]][period_time] = {}
				playsJSON[period_dict[period]][period_time]["Scorer"] = goal_info["Scorer"]
				playsJSON[period_dict[period]][period_time]["Assist 1"] = goal_info["Assist 1"]
				playsJSON[period_dict[period]][period_time]["Assist 2"] = goal_info["Assist 2"]

				playsJSON[period_dict[period]][period_time]["Scorer"] += " " + record[0]
				playsJSON[period_dict[period]][period_time]["Assist 1"] += " " + record[1]
				playsJSON[period_dict[period]][period_time]["Assist 2"] += " " + record[2]

				if (plays.iloc[i]["team_id_for"] == game.iloc[0]["home_team_id"]):
					playsJSON[period_dict[period]][period_time]["Home Team"] = team_data[team_data["team_id"] == plays.iloc[i]["team_id_for"]].iloc[0]["abbreviation"]
					playsJSON[period_dict[period]][period_time]["Away Team"] = team_data[team_data["team_id"] == plays.iloc[i]["team_id_against"]].iloc[0]["abbreviation"]
				else:
					playsJSON[period_dict[period]][period_time]["Away Team"] = team_data[team_data["team_id"] == plays.iloc[i]["team_id_for"]].iloc[0]["abbreviation"]
					playsJSON[period_dict[period]][period_time]["Home Team"] = team_data[team_data["team_id"] == plays.iloc[i]["team_id_against"]].iloc[0]["abbreviation"]

				playsJSON[period_dict[period]][period_time]["Away Team Score"] = int(plays.iloc[i]["goals_away"])
				playsJSON[period_dict[period]][period_time]["Home Team Score"] = int(plays.iloc[i]["goals_home"])

			elif int(plays.iloc[i]["period"]) != period:
				period += 1

	return jsonify(playsJSON)

def player_record(desc_list):
	ret_list = []

	for i in desc_list:
		if i[0] == '(':
			ret_list.append(i[0:3])
	if len(ret_list) == 2:
		ret_list.append("")
	elif len(ret_list) == 1:
		ret_list.append("")
		ret_list.append("")
	return ret_list

def find_goal_info(play_id):
	goal_info = game_plays_players_data[game_plays_players_data["play_id"] == play_id]
	assists = 0
	goal_info_dict = {"Scorer": "", "Assist 1": "Unassisted", "Assist 2": ""}

	for i in range(goal_info.shape[0]):
		if goal_info.iloc[i]["playerType"] == "Scorer":
			playerFirstName = player_info[goal_info.iloc[i]["player_id"] == player_info["player_id"]].iloc[0]["firstName"]
			playerLastName = player_info[goal_info.iloc[i]["player_id"] == player_info["player_id"]].iloc[0]["lastName"]
			goal_info_dict["Scorer"] = playerFirstName + " " + playerLastName
		elif goal_info.iloc[i]["playerType"] == "Assist":
			playerFirstName = player_info[goal_info.iloc[i]["player_id"] == player_info["player_id"]].iloc[0]["firstName"]
			playerLastName = player_info[goal_info.iloc[i]["player_id"] == player_info["player_id"]].iloc[0]["lastName"]
			if (assists == 0):
				goal_info_dict["Assist 1"] = playerFirstName + " " + playerLastName
				assists += 1
			else:
				goal_info_dict["Assist 2"] = playerFirstName + " " + playerLastName

	# print(goal_info_dict)
	return goal_info_dict

def outcome_simplifier(s):
    if "REG" in s:
        return "FINAL"
    elif "OT" in s:
        return "FINAL/OT"

    return -1

if __name__ == '__main__':
    app.run(debug=True)