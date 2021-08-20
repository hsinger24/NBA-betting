import pandas as pd
import datetime as dt
import numpy as np
from nba_api.stats.endpoints import boxscoreadvancedv2
from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.endpoints import cumestatsteam

def retrieve_advanced_stats(year, continue_value = None):
    if continue_value is None:
        game_ids = list(range(1,1231))
        games_df_2007 = pd.DataFrame()
    if continue_value is not None:
        games_df_2007 = pd.read_csv('Data/api_data_' + str(year) + '_advanced.csv', index_col = 0)
        game_ids = list(range(continue_value,1231))
    for game in game_ids:
        try:
            game = str(game)
            if len(game)==1:
                game_id = '00207' + '0000' + game
            if len(game)==2:
                game_id = '00207' + '000' + game
            if len(game)==3:
                game_id = '00207' + '00' + game
            if len(game)==4:
                game_id = '00207' + '0' + game
            box_score = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id = game_id)
            box_df = box_score.get_data_frames()[1]
            games_df_2007 = games_df_2007.append(box_df)
        except:
            print(game, 'advanced')
            break
    games_df_2007.reset_index(drop = True, inplace = True)
    games_df_2007.to_csv('api_data_' + str(year) + '_advanced.csv')
    return

def retrieve_traditional_stats(year, continue_value = None):
    if continue_value is None:
        game_ids = list(range(1,1231))
        games_df_2007 = pd.DataFrame()
    if continue_value is not None:
        games_df_2007 = pd.read_csv('Data/api_data_' + str(year) + '_traditional.csv', index_col = 0)
        game_ids = list(range(continue_value,1231))
    for game in game_ids:
        try:
            game = str(game)
            if len(game)==1:
                game_id = '00207' + '0000' + game
            if len(game)==2:
                game_id = '00207' + '000' + game
            if len(game)==3:
                game_id = '00207' + '00' + game
            if len(game)==4:
                game_id = '00207' + '0' + game
            box_score = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id = game_id)
            box_df = box_score.get_data_frames()[1]
            games_df_2007 = games_df_2007.append(box_df)
        except:
            print(game, 'traditional')
            break
    games_df_2007.reset_index(drop = True, inplace = True)
    games_df_2007.to_csv('api_data_' + str(year) + '_traditional.csv')
    return

