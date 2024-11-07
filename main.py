from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
import time

def get_player_id(player_name):
    # Search for player ID based on the player's name
    player = players.find_players_by_full_name(player_name)
    if player:
        return player[0]['id']
    else:
        print("Player not found.")
        return None

def get_last_5_games_stats(player_name):
    player_id = get_player_id(player_name)
    if player_id is None:
        return

    # Get the game log for the player
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2024')
    games_df = gamelog.get_data_frames()[0]  # Get data as a DataFrame

    # Filter for only the last 5 games and create a full copy
    last_5_stats = games_df.head(5).copy()

    # Extract points, rebounds, and assists for each game
    last_5_stats = last_5_stats[['GAME_DATE', 'PTS', 'REB', 'AST']]
    last_5_stats.columns = ['Date', 'Points', 'Rebounds', 'Assists']

    # Calculate combined Points + Rebounds + Assists (PRA)
    last_5_stats['PRA'] = last_5_stats['Points'] + last_5_stats['Rebounds'] + last_5_stats['Assists']

    # Calculate variance and standard deviation for the combined PRA
    variance_pra = last_5_stats['PRA'].var()
    std_dev_pra = last_5_stats['PRA'].std()

    # Determine consistency level based on standard deviation
    if std_dev_pra < 8:
        consistency = "Good"
    elif 8 <= std_dev_pra < 10:
        consistency = "Moderate"
    else:
        consistency = "Poor"

    # Display last 5 game stats with combined PRA, variance, and standard deviation
    print(f"{player_name}: {std_dev_pra:.2f} ({consistency})")

with open("players.txt", "r") as file:
    player_names = [line.strip() for line in file.readlines()]

for player_name in player_names:
    get_last_5_games_stats(player_name)
    time.sleep(3)