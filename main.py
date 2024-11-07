from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
import time
import itertools
import threading
import sys

player_stats_df = pd.DataFrame(columns=['Player', 'Standard Deviation'])
progress = 0  # Track the number of players processed
total_players = 0  # Will hold the total number of players

# Function to display loading animation with progress percentage
def loading_animation():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if not loading:
            break
        percentage = (progress / total_players) * 100
        sys.stdout.write(f'\rProcessing... {c} {percentage:.1f}% completed')
        sys.stdout.flush()
        time.sleep(0.2)

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

    if games_df.empty:  # Check if there is any game data
        return

    # Filter for only the last 5 games and create a full copy
    last_5_stats = games_df.head(5).copy()

    # Extract points, rebounds, and assists for each game
    last_5_stats = last_5_stats[['GAME_DATE', 'PTS', 'REB', 'AST']]
    last_5_stats.columns = ['Date', 'Points', 'Rebounds', 'Assists']

    # Calculate combined Points + Rebounds + Assists (PRA)
    last_5_stats['PRA'] = last_5_stats['Points'] + last_5_stats['Rebounds'] + last_5_stats['Assists']

    # Calculate variance and standard deviation for the combined PRA
    std_dev_pra = last_5_stats['PRA'].std()
    
    return player_name, std_dev_pra

player_names = []
with open("players.txt", "r") as file:
    player_names = [line.strip() for line in file.readlines()]

# Set the total number of players for percentage calculation
total_players = len(player_names)

loading = True
loading_thread = threading.Thread(target=loading_animation)
loading_thread.start()

for player_name in player_names:
    player_name, std_dev_pra = get_last_5_games_stats(player_name)
    player_stats_df = player_stats_df._append({'Player': player_name, 'Standard Deviation': std_dev_pra}, ignore_index=True)
    progress += 1
    time.sleep(0.5)

loading = False
loading_thread.join()
sys.stdout.write('\rProcessing complete!          \n')
sys.stdout.flush()

player_stats_df = player_stats_df.sort_values(by="Standard Deviation", ascending=True)

# Display the first 10 entries
print("Top 15 Players with the Least Deviation:")
print(player_stats_df.head(15))