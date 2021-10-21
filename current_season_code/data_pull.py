import pandas as pd
import datetime as dt
import numpy as np
from nba_api.stats.endpoints import boxscoreadvancedv2
from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.endpoints import cumestatsteam

def retrieve_advanced_stats(year, continue_value = None):
    """Retrieves advanced stats from NBA api for given year. NEED TO ADJUST GAME ID MANUALLY

    Args:
        year: the year of interest
        continue_value: The value of game_id to start at if function did not run all the way through prior

    Returns:
        Advanced stats df for a given year
    """
    if continue_value is None:
        game_ids = list(range(1,1231))
        games_df_2021 = pd.DataFrame()
    if continue_value is not None:
        games_df_2021 = pd.read_csv('data/api_data_' + str(year) + '_advanced.csv', index_col = 0)
        game_ids = list(range(continue_value,1231))
    for game in game_ids:
        try:
            game = str(game)
            if len(game)==1:
                game_id = '00221' + '0000' + game
            if len(game)==2:
                game_id = '00221' + '000' + game
            if len(game)==3:
                game_id = '00221' + '00' + game
            if len(game)==4:
                game_id = '00221' + '0' + game
            box_score = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id = game_id)
            box_df = box_score.get_data_frames()[1]
            games_df_2021 = games_df_2021.append(box_df)
        except:
            print(game, 'advanced')
            break
    games_df_2021.reset_index(drop = True, inplace = True)
    games_df_2021.to_csv('current_season_data/api_data_' + str(year) + '_advanced.csv')
    return

def retrieve_traditional_stats(year, continue_value = None):
    """Retrieves traditional stats from NBA api for given year. NEED TO ADJUST GAME ID MANUALLY

    Args:
        year: the year of interest
        continue_value: The value of game_id to start at if function did not run all the way through prior

    Returns:
        Traditional stats df for a given year
    """
    if continue_value is None:
        game_ids = list(range(1,1231))
        games_df_2021 = pd.DataFrame()
    if continue_value is not None:
        games_df_2021 = pd.read_csv('data/api_data_' + str(year) + '_traditional.csv', index_col = 0)
        game_ids = list(range(continue_value,1231))
    for game in game_ids:
        try:
            game = str(game)
            if len(game)==1:
                game_id = '00221' + '0000' + game
            if len(game)==2:
                game_id = '00221' + '000' + game
            if len(game)==3:
                game_id = '00221' + '00' + game
            if len(game)==4:
                game_id = '00221' + '0' + game
            box_score = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id = game_id)
            box_df = box_score.get_data_frames()[1]
            games_df_2021 = games_df_2021.append(box_df)
        except:
            print(game, 'traditional')
            break
    games_df_2021.reset_index(drop = True, inplace = True)
    games_df_2021.to_csv('current_season_data/api_data_' + str(year) + '_traditional.csv')
    return