import pandas as pd
import datetime as dt
import numpy as np
import time
import re
import json
import unidecode
import re
from nba_api.stats.endpoints import boxscoreadvancedv2
from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.endpoints import cumestatsteam
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

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
        games_df_2021 = pd.read_csv('current_season_data/api_data_' + str(year) + '_advanced.csv', index_col = 0)
        game_ids = list(range(continue_value,(continue_value+18)))
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
            box_df['Date'] = dt.date.today() - dt.timedelta(days = 1)
            games_df_2021 = games_df_2021.append(box_df)
        except:
            print(game, 'advanced')
            break
    games_df_2021.reset_index(drop = True, inplace = True)
    games_df_2021 = games_df_2021.drop_duplicates(subset = ['GAME_ID', 'TEAM_NAME'])
    games_df_2021.dropna(inplace = True)
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
        games_df_2021 = pd.read_csv('current_season_data/api_data_' + str(year) + '_traditional.csv', index_col = 0)
        game_ids = list(range(continue_value,(continue_value+18)))
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
    games_df_2021 = games_df_2021.drop_duplicates(subset = ['GAME_ID', 'TEAM_NAME'])
    games_df_2021.dropna(inplace = True)
    games_df_2021.reset_index(drop = True, inplace = True)
    games_df_2021.to_csv('current_season_data/api_data_' + str(year) + '_traditional.csv')
    return

def format_api_data(year):
    """Calls in the advanced and traditional API data for a given year, then formats the data for the next step

    Args:
       year: the year of API data we want to retrieve

    Returns:
        DataFrame with formatted API data
    """
    # Reading in data
    advanced = pd.read_csv('current_season_data/api_data_' + str(year) + '_advanced.csv', index_col = 0)
    traditional = pd.read_csv('current_season_data/api_data_' + str(year) + '_traditional.csv', index_col = 0)

    #Merging data, dropping unnecessary columns, renaming columns

    merged = pd.merge(traditional, advanced, on = ['GAME_ID', 'TEAM_NAME'])
    merged.drop(['TEAM_ABBREVIATION_x', 'TEAM_CITY_x', 'MIN_x', 'TEAM_ID_y', 'TEAM_ABBREVIATION_y', 'TEAM_CITY_y',
                'MIN_y'], axis = 1, inplace = True)
    merged.columns = ['GAME_ID', 'TEAM_ID', 'TEAM_NAME', 'FGM', 'FGA', 'FG_PCT', 'FG3M',
        'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST',
        'STL', 'BLK', 'TO', 'PF', 'PTS', 'PLUS_MINUS', 'E_OFF_RATING',
        'OFF_RATING', 'E_DEF_RATING', 'DEF_RATING', 'E_NET_RATING',
        'NET_RATING', 'AST_PCT', 'AST_TOV', 'AST_RATIO', 'OREB_PCT', 'DREB_PCT',
        'REB_PCT', 'E_TM_TOV_PCT', 'TM_TOV_PCT', 'EFG_PCT', 'TS_PCT', 'USG_PCT',
        'E_USG_PCT', 'E_PACE', 'PACE', 'PACE_PER40', 'POSS', 'PIE', 'Date']

    # Joining data to itself to have one row per game
    evens = merged.iloc[::2]
    evens.reset_index(drop = True, inplace = True)
    odds = merged.iloc[1::2]
    odds.reset_index(drop = True, inplace = True)
    final = pd.merge(evens, odds, left_on = evens.index, right_on = odds.index)
    final.drop('key_0', axis = 1, inplace = True)

    # Tracking how many wins and losses a team has in the given season
    final['Team_1_wins'] = 0
    final['Team_1_losses'] = 0
    final['Team_2_wins'] = 0
    final['Team_2_losses'] = 0
    record_dict = {}
    teams = set(list(final.TEAM_NAME_x.unique()) + list(final.TEAM_NAME_y.unique()))
    for team in teams:
        record_dict[team + '_wins'] = 0.0
        record_dict[team + '_losses'] = 0.0
    for index, row in final.iterrows():
        if row.PTS_x>row.PTS_y:
            record_dict[row.TEAM_NAME_x + "_wins"] += 1.0
            record_dict[row.TEAM_NAME_y + "_losses"] += 1.0
        if row.PTS_x<row.PTS_y:
            record_dict[row.TEAM_NAME_x + "_losses"] += 1.0
            record_dict[row.TEAM_NAME_y + "_wins"] += 1.0
        final.loc[index, 'Team_1_wins'] = record_dict[row.TEAM_NAME_x + "_wins"]
        final.loc[index, 'Team_1_losses'] = record_dict[row.TEAM_NAME_x + "_losses"]
        final.loc[index, 'Team_2_wins'] = record_dict[row.TEAM_NAME_y + "_wins"]
        final.loc[index, 'Team_2_losses'] = record_dict[row.TEAM_NAME_y + "_losses"]
    final['Team_1_win_pct'] = final.Team_1_wins/(final.Team_1_wins + final.Team_1_losses)
    final['Team_2_win_pct'] = final.Team_2_wins/(final.Team_2_wins + final.Team_2_losses)

    # Reformatting columns
    final = final[['GAME_ID_x', 'TEAM_NAME_x', 'TEAM_NAME_y','FGM_x', 'FGA_x', 'FG_PCT_x',
        'FG3M_x', 'FG3A_x', 'FG3_PCT_x', 'FTM_x', 'FTA_x', 'FT_PCT_x', 'OREB_x',
        'DREB_x', 'REB_x', 'AST_x', 'STL_x', 'BLK_x', 'TO_x', 'PF_x', 'PTS_x',
        'PLUS_MINUS_x', 'E_OFF_RATING_x', 'OFF_RATING_x', 'E_DEF_RATING_x',
        'DEF_RATING_x', 'E_NET_RATING_x', 'NET_RATING_x', 'AST_PCT_x',
        'AST_TOV_x', 'AST_RATIO_x', 'OREB_PCT_x', 'DREB_PCT_x', 'REB_PCT_x',
        'E_TM_TOV_PCT_x', 'TM_TOV_PCT_x', 'EFG_PCT_x', 'TS_PCT_x', 'USG_PCT_x',
        'E_USG_PCT_x', 'E_PACE_x', 'PACE_x', 'PACE_PER40_x', 'POSS_x', 'PIE_x', 'Date_x',
        'GAME_ID_y', 'TEAM_ID_y', 'FGM_y', 'FGA_y', 'FG_PCT_y',
        'FG3M_y', 'FG3A_y', 'FG3_PCT_y', 'FTM_y', 'FTA_y', 'FT_PCT_y', 'OREB_y',
        'DREB_y', 'REB_y', 'AST_y', 'STL_y', 'BLK_y', 'TO_y', 'PF_y', 'PTS_y',
        'PLUS_MINUS_y', 'E_OFF_RATING_y', 'OFF_RATING_y', 'E_DEF_RATING_y',
        'DEF_RATING_y', 'E_NET_RATING_y', 'NET_RATING_y', 'AST_PCT_y',
        'AST_TOV_y', 'AST_RATIO_y', 'OREB_PCT_y', 'DREB_PCT_y', 'REB_PCT_y',
        'E_TM_TOV_PCT_y', 'TM_TOV_PCT_y', 'EFG_PCT_y', 'TS_PCT_y', 'USG_PCT_y',
        'E_USG_PCT_y', 'E_PACE_y', 'PACE_y', 'PACE_PER40_y', 'POSS_y', 'PIE_y', 'Date_y',
        'Team_1_wins', 'Team_1_losses', 'Team_2_wins', 'Team_2_losses',
        'Team_1_win_pct', 'Team_2_win_pct']]

    return final

def formatted_data_1(formatted_api_data):
    '''
    Further reformats the column names and merges with the odds table
    Params:
        - formatted_api_data: combined advanced/traditional API stats for that game
    Returns:
        - Game's data merged with odds for that game
    '''

    # Calling in previously formatted data
    existing_data = pd.read_csv('current_season_data/formatted_data_1.csv', index_col = 0)

    # Adjusting the column names of previous step formatting (API)
    formatted_api_data.drop_duplicates(subset = ['GAME_ID_x'], inplace = True)
    formatted_api_data.reset_index(drop = True, inplace = True)
    columns = list(formatted_api_data.columns)
    data = formatted_api_data[['Date_y']+columns[:-7]+columns[-6:]]
    columns = ['Date', 'GAME_ID', 'TEAM_NAME', 'TEAM_NAME_Opp', 'FGM', 'FGA',
        'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
        'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK',
        'TO', 'PF', 'PTS', 'PLUS_MINUS', 'E_OFF_RATING',
        'OFF_RATING', 'E_DEF_RATING', 'DEF_RATING', 'E_NET_RATING',
        'NET_RATING', 'AST_PCT', 'AST_TOV', 'AST_RATIO', 'OREB_PCT',
        'DREB_PCT', 'REB_PCT', 'E_TM_TOV_PCT', 'TM_TOV_PCT',
        'EFG_PCT', 'TS_PCT', 'USG_PCT', 'E_USG_PCT', 'E_PACE',
        'PACE', 'PACE_PER40', 'POSS', 'PIE', 'drop_1', 'drop_2',
        'drop_3', 'FGM_Opp', 'FGA_Opp', 'FG_PCT_Opp', 'FG3M_Opp', 'FG3A_Opp',
        'FG3_PCT_Opp', 'FTM_Opp', 'FTA_Opp', 'FT_PCT_Opp', 'OREB_Opp', 'DREB_Opp', 'REB_Opp',
        'AST_Opp', 'STL_Opp', 'BLK_Opp', 'TO_Opp', 'PF_Opp', 'PTS_Opp', 'PLUS_MINUS_Opp',
        'E_OFF_RATING_Opp', 'OFF_RATING_Opp', 'E_DEF_RATING_Opp', 'DEF_RATING_Opp',
        'E_NET_RATING_Opp', 'NET_RATING_Opp', 'AST_PCT_Opp', 'AST_TOV_Opp',
        'AST_RATIO_Opp', 'OREB_PCT_Opp', 'DREB_PCT_Opp', 'REB_PCT_Opp',
        'E_TM_TOV_PCT_Opp', 'TM_TOV_PCT_Opp', 'EFG_PCT_Opp', 'TS_PCT_Opp', 'USG_PCT_Opp',
        'E_USG_PCT_Opp', 'E_PACE_Opp', 'PACE_Opp', 'PACE_PER40_Opp', 'POSS_Opp', 'PIE_Opp',
        'Wins', 'Losses', 'Wins_Opp', 'Losses_Opp',
        'Win_Pct', 'Win_Pct_Opp']
    data.columns = columns

    # Calling in the odds for yesterday's games
    odds_yesterday = pd.read_csv('current_season_data/yesterday_odds.csv', index_col = 0)
    odds_yesterday['GAME_ID'] = 0

    # Subsetting API formatted data to only include yesterday's games
    yesterday = dt.date.today() - dt.timedelta(days = 1)
    yesterday = str(yesterday)
    yesterday_formatted = data[data.Date==yesterday]

    # Getting correct GAME_ID for yesterday's odds to merge with data
    teams = list(yesterday_formatted['TEAM_NAME'])
    teams_opp = list(yesterday_formatted['TEAM_NAME_Opp'])
    for index, row in odds_yesterday.iterrows():
        if row.Home_Team in teams:
            location = teams.index(row.Home_Team)
            team = teams[location]
            game_id = yesterday_formatted[yesterday_formatted.TEAM_NAME==team]['GAME_ID'].values[0]
            odds_yesterday.loc[index, 'GAME_ID'] = game_id
        else:
            location = teams_opp.index(row.Home_Team)
            team = teams[location]
            game_id = yesterday_formatted[yesterday_formatted.TEAM_NAME==team]['GAME_ID'].values[0]
            odds_yesterday.loc[index, 'GAME_ID'] = game_id

    # Merging odds with data and adjusting column names
    merged = pd.merge(yesterday_formatted, odds_yesterday, on = 'GAME_ID')
    columns = list(merged.columns)
    merged = merged[['GAME_ID', 'Date_x', 'Away_Team', 'Home_Odds', 'Home_Team', 'Away_Odds']+columns[1:-7]]
    merged = merged.loc[:,~merged.columns.duplicated()]
    merged.columns = ['Game_ID', 'Date', 'Away_Team', 'ML_Home', 'Home_Team', 'ML_Away', 'Team', 'Team_Opp',
        'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB','REB', 'AST',
        'STL', 'BLK', 'TO', 'PF', 'PTS', 'PLUS_MINUS', 'E_OFF_RATING', 'OFF_RATING', 'E_DEF_RATING', 'DEF_RATING',
        'E_NET_RATING', 'NET_RATING', 'AST_PCT', 'AST_TOV', 'AST_RATIO', 'OREB_PCT', 'DREB_PCT', 'REB_PCT', 'E_TM_TOV_PCT',
        'TM_TOV_PCT', 'EFG_PCT', 'TS_PCT', 'USG_PCT', 'E_USG_PCT', 'E_PACE', 'PACE', 'PACE_PER40', 'POSS', 'PIE',
        'drop_1', 'drop_2', 'drop_3','FGM_Opp', 'FGA_Opp', 'FG_PCT_Opp', 'FG3M_Opp','FG3A_Opp', 'FG3_PCT_Opp',
        'FTM_Opp','FTA_Opp', 'FT_PCT_Opp', 'OREB_Opp', 'DREB_Opp', 'REB_Opp', 'AST_Opp','STL_Opp', 'BLK_Opp', 'TO_Opp',
        'PF_Opp', 'PTS_Opp', 'PLUS_MINUS_Opp', 'E_OFF_RATING_Opp', 'OFF_RATING_Opp', 'E_DEF_RATING_Opp', 'DEF_RATING_Opp',
        'E_NET_RATING_Opp', 'NET_RATING_Opp', 'AST_PCT_Opp', 'AST_TOV_Opp', 'AST_RATIO_Opp', 'OREB_PCT_Opp', 'DREB_PCT_Opp',
        'REB_PCT_Opp', 'E_TM_TOV_PCT_Opp', 'TM_TOV_PCT_Opp', 'EFG_PCT_Opp', 'TS_PCT_Opp', 'USG_PCT_Opp', 'E_USG_PCT_Opp',
        'E_PACE_Opp', 'PACE_Opp', 'PACE_PER40_Opp', 'POSS_Opp', 'PIE_Opp', 'Wins', 'Losses', 'Wins_Opp', 'Losses_Opp',
        'Win_Pct', 'Win_Pct_Opp']
    merged.drop(['drop_1', 'drop_2', 'drop_3'], axis = 1, inplace = True)

    # Appending yesterday's data with season up to this point and re-writing file
    final = existing_data.append(merged)
    final.reset_index(drop = True, inplace = True)
    final.to_csv('current_season_data/formatted_data_1.csv')
    return final

def formatted_data_2():
    '''
    Takes in formatted API data merged with odds, adds additional stats + cumulative stats
    Returns:
        - Stats formatted in their final form
    '''

    team_map = {
    'WAS' : 'Wizards',
    'BOS' : 'Celtics',
    'NOP' : 'Pelicans',
    'NYK' : 'Knicks',
    'DET' : 'Pistons',
    'ORL' : 'Magic',
    'PHI' : '76ers',
    'ATL' : 'Hawks',
    'IND' : 'Pacers',
    'TOR' : 'Raptors',
    'MEM' : 'Grizzlies',
    'MIA' : 'Heat',
    'CHI' : 'Bulls',
    'UTA' : 'Jazz',
    'MIL' : 'Bucks',
    'SAS' : 'Spurs',
    'GSW' : 'Warriors',
    'OKC' : 'Thunder',
    'MIN' : 'Timberwolves',
    'DEN' : 'Nuggets',
    'PHX' : 'Suns',
    'CLE' : 'Cavaliers',
    'DAL' : 'Mavericks',
    'SAC' : 'Kings',
    'CHA' : 'Hornets',
    'POR' : 'Trail Blazers',
    'BKN' : 'Nets',
    'LAL' : 'Lakers',
    'LAC' : 'Clippers',
    'HOU' : 'Rockets'
    }

    # Add B2B, days rest, home stats to formatted API data
    test = pd.read_csv('current_season_data/formatted_data_1.csv', index_col = 0)
    test['Date'] = pd.to_datetime(test.Date)
    test['is_B2B'] = 0
    test['is_B2B_Opp'] = 0
    test['is_B2B_First'] = 0
    test['is_B2B_First_Opp'] = 0
    test['is_B2B_Second'] = 0
    test['is_B2B_Second_Opp'] = 0
    test['Days_Rest_Team'] = 0
    test['Days_Next Game'] = 0
    test['Days_Rest_Team_Opp'] = 0
    test['Days_Next Game_Opp'] = 0
    test['is_Home'] = 0
    test['is_Home_Opp'] = 0
    for index, row in test.iterrows():
        if row.Home_Team == row.Team:
            test.loc[index, 'is_Home'] = 1
            test.loc[index, 'is_Home_Opp'] = 0
            continue
        else:
            test.loc[index, 'is_Home_Opp'] = 1
            test.loc[index, 'is_Home'] = 0
            continue
    for index, row in test.iterrows():
        team = row.Team
        df_1 = test[(test.Team == team) | (test.Team_Opp == team)]
        df_1.reset_index(inplace = True)
        df_1.reset_index(inplace = True)
        df_1.rename(columns = {'level_0': 'Game_Number'}, inplace = True)
        df_1['Game_Number'] = df_1.Game_Number + 1
        row_2 = df_1.loc[df_1['index']==index, :]
        game_number = row_2['Game_Number'].values[0]
        day = row_2['Date'].values[0]
        row_prior = df_1[df_1['Game_Number']==(game_number-1)]
        if len(row_prior) != 0:
            day_prior = row_prior['Date'].values[0]
        row_after = df_1[df_1['Game_Number']==(game_number+1)]
        if len(row_after) != 0:
            day_after = row_after['Date'].values[0]
        if game_number == 1:
            test.loc[index, 'is_B2B'] = 0
            test.loc[index, 'Days_Rest_Team'] = 0
            continue
        try:
            test.loc[index, 'Days_Rest_Team'] = int(day-day_prior)/86400000000000
        except:
            test.loc[index, 'Days_Rest_Team'] = 0
        try:
            test.loc[index, 'Days_Next Game'] = int(day_after-day)/86400000000000
        except:
            test.loc[index, 'Days_Next Game'] = 0
        if len(row_prior) != 0:
            if (int(day-day_prior)) == (172800000000000/2):
                test.loc[index, 'is_B2B'] = 1
                test.loc[index, 'is_B2B_Second'] = 1
        if len(row_after) != 0:
            if (int(day-day_after)) == (-172800000000000/2):
                test.loc[index, 'is_B2B'] = 1
                test.loc[index, 'is_B2B_First'] = 1
        else:
            continue
    
    # Adding same B2B, home, rest stats for the opponent
    for index, row in test.iterrows():
        team_Opp = row.Team_Opp
        df_1 = test[(test.Team == team_Opp) | (test.Team_Opp == team_Opp)]
        df_1.reset_index(inplace = True)
        df_1.reset_index(inplace = True)
        df_1.rename(columns = {'level_0': 'Game_Number'}, inplace = True)
        df_1['Game_Number'] = df_1.Game_Number + 1
        row_2 = df_1.loc[df_1['index']==index, :]
        game_number = row_2['Game_Number'].values[0]
        day = row_2['Date'].values[0]
        row_prior = df_1[df_1['Game_Number']==(game_number-1)]
        if len(row_prior) != 0:
            day_prior = row_prior['Date'].values[0]
        row_after = df_1[df_1['Game_Number']==(game_number+1)]
        if len(row_after) != 0:
            day_after = row_after['Date'].values[0]
        if game_number == 0:
            test.loc[index, 'is_B2B_Opp'] = 0
            test.loc[index, 'Days_Rest_Team_Opp'] = 0
            continue
        try:
            test.loc[index, 'Days_Rest_Team_Opp'] = int(day-day_prior)/86400000000000
        except:
            test.loc[index, 'Days_Rest_Team_Opp'] = 0
        try:
            test.loc[index, 'Days_Next Game_Opp'] = int(day_after-day)/86400000000000
        except:
            test.loc[index, 'Days_Next Game_Opp'] = 0
        if len(row_prior) != 0:
            if (int(day-day_prior)) == (172800000000000/2):
                test.loc[index, 'is_B2B_Opp'] = 1
                test.loc[index, 'is_B2B_Second_Opp'] = 1
        if len(row_after) != 0:
            if (int(day-day_after)) == (-172800000000000/2):
                test.loc[index, 'is_B2B_Opp'] = 1
                test.loc[index, 'is_B2B_First_Opp'] = 1
        else:
            continue
    
    # Reformatting columns
    test = test[['Game_ID', 'Date', 'Team', 'Team_Opp', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA','FT_PCT', 'OREB',
    'DREB','REB', 'AST', 'STL', 'BLK', 'TO', 'PF', 'PTS', 'PLUS_MINUS', 'E_OFF_RATING', 'OFF_RATING', 'E_DEF_RATING',
    'DEF_RATING', 'E_NET_RATING', 'NET_RATING', 'AST_PCT', 'AST_TOV', 'AST_RATIO', 'OREB_PCT', 'DREB_PCT', 'REB_PCT',
    'E_TM_TOV_PCT', 'TM_TOV_PCT', 'EFG_PCT', 'TS_PCT', 'USG_PCT', 'E_USG_PCT', 'E_PACE', 'PACE', 'PACE_PER40', 'POSS',
    'PIE', 'Wins', 'Losses', 'Win_Pct', 'is_B2B', 'is_B2B_First', 'is_B2B_Second', 'Days_Rest_Team', 'Days_Next Game', 'is_Home', 'FGM_Opp', 'FGA_Opp', 'FG_PCT_Opp', 'FG3M_Opp', 'FG3A_Opp', 'FG3_PCT_Opp', 'FTM_Opp',
    'FTA_Opp', 'FT_PCT_Opp', 'OREB_Opp', 'DREB_Opp', 'REB_Opp', 'AST_Opp', 'STL_Opp', 'BLK_Opp', 'TO_Opp', 'PF_Opp',
    'PTS_Opp', 'PLUS_MINUS_Opp', 'E_OFF_RATING_Opp', 'OFF_RATING_Opp', 'E_DEF_RATING_Opp', 'DEF_RATING_Opp',
    'E_NET_RATING_Opp', 'NET_RATING_Opp', 'AST_PCT_Opp', 'AST_TOV_Opp', 'AST_RATIO_Opp', 'OREB_PCT_Opp',
    'DREB_PCT_Opp', 'REB_PCT_Opp', 'E_TM_TOV_PCT_Opp', 'TM_TOV_PCT_Opp', 'EFG_PCT_Opp', 'TS_PCT_Opp', 'USG_PCT_Opp',
    'E_USG_PCT_Opp', 'E_PACE_Opp', 'PACE_Opp', 'PACE_PER40_Opp', 'POSS_Opp', 'PIE_Opp', 'Wins_Opp', 'Losses_Opp',
    'Win_Pct_Opp', 'is_B2B_Opp', 'is_B2B_First_Opp', 'is_B2B_Second_Opp', 'Days_Rest_Team_Opp', 'Days_Next Game_Opp',
    'is_Home_Opp']]

    # Furthering creation of new stats columns and formatting 

    stats = test.copy()

    # Getting columns to be adjusted to per 100
    all_columns = list(stats.columns)
    cols_team = all_columns[4:7] + all_columns[7:10] + all_columns[10:12] + all_columns[12:23]
    for col in cols_team:
        stats[col + '_Per100'] = (stats[col]/stats['POSS'])*100
    cols_opp = all_columns[55:58] + all_columns[58:61] + all_columns[61:63] + all_columns[63:74]

    # Calculating the per 100 statistics
    for col in cols_opp:
        stats[col[:-4] + '_Per100' + col[-4:]] = (stats[col]/stats['POSS_Opp'])*100

    # Adjusting stats df to only get desired columns
    cols_of_interest = ['Game_ID', 'Date', 'Team', 'Team_Opp', 'FGM_Per100', 'FGA_Per100', 'FG_PCT', 
                'FG3M_Per100', 'FG3A_Per100', 'FG3_PCT', 'FTM_Per100', 'FTA_Per100', 'FT_PCT', 
                'OREB_Per100', 'DREB_Per100', 'REB_Per100', 'AST_Per100', 'STL_Per100', 'BLK_Per100', 
                'TO_Per100', 'PF_Per100', 'PTS_Per100', 'PLUS_MINUS_Per100', 'E_OFF_RATING', 'OFF_RATING', 
                'E_DEF_RATING', 'DEF_RATING', 'E_NET_RATING', 'NET_RATING', 'AST_PCT', 'AST_TOV', 'AST_RATIO', 
                'OREB_PCT', 'DREB_PCT', 'REB_PCT', 'E_TM_TOV_PCT', 'TM_TOV_PCT', 'EFG_PCT', 'TS_PCT', 'USG_PCT', 
                'E_USG_PCT', 'E_PACE', 'PACE', 'PACE_PER40', 'POSS', 'PIE', 'Wins', 'Losses', 'Win_Pct', 'is_B2B', 
                'is_B2B_First', 'is_B2B_Second', 'Days_Rest_Team', 'Days_Next Game', 'is_Home']
    for col in cols_of_interest[4:]:
        cols_of_interest.append(col+'_Opp')
    stats = stats[cols_of_interest]

    # Calculating aggregated stats
    columns = list(stats.columns)
    cols_of_interest = columns[4:46]
    teams = [value for key, value in team_map.items()]
    for col in cols_of_interest:
        stats[col + '_Agg'] = 0
        stats[col + '_Agg' + '_Opp'] = 0
        for team in teams:
            df_team = stats[(stats.Team==team) | (stats.Team_Opp==team)]
            df_team['stat_of_interest'] = np.NaN
            for index, row in df_team.iterrows():
                if row['Team'] == team:
                    df_team.loc[index, 'stat_of_interest'] = row[col]
                    stat_col = df_team['stat_of_interest']
                    stats.loc[index, col + '_Agg'] = stat_col.mean()
                    # df_team.loc[index, 'stat_of_interest'] = row[col]
                else:
                    df_team.loc[index, 'stat_of_interest'] = row[col + '_Opp']
                    stat_col = df_team['stat_of_interest']
                    stats.loc[index, col + '_Agg' + '_Opp'] = stat_col.mean()
                    # df_team.loc[index, 'stat_of_interest'] = row[col + '_Opp']

    # Getting desired columns
    cols_of_interest = ['Game_ID', 'Date', 'Team', 'Team_Opp', 'FGM_Per100_Agg', 'FGA_Per100_Agg', 'FG_PCT_Agg', 
                        'FG3M_Per100_Agg',  'FG3A_Per100_Agg',  'FG3_PCT_Agg', 'FTM_Per100_Agg', 'FTA_Per100_Agg',
                        'FT_PCT_Agg', 'OREB_Per100_Agg', 'DREB_Per100_Agg', 'REB_Per100_Agg', 'AST_Per100_Agg',
                        'STL_Per100_Agg', 'BLK_Per100_Agg', 'TO_Per100_Agg', 'PF_Per100_Agg', 'PTS_Per100_Agg', 
                        'PLUS_MINUS_Per100_Agg', 'E_OFF_RATING_Agg', 'OFF_RATING_Agg', 'E_DEF_RATING_Agg', 
                        'DEF_RATING_Agg', 'E_NET_RATING_Agg', 'NET_RATING_Agg', 'AST_PCT_Agg', 'AST_TOV_Agg', 
                        'AST_RATIO_Agg', 'OREB_PCT_Agg', 'DREB_PCT_Agg', 'REB_PCT_Agg', 'E_TM_TOV_PCT_Agg', 
                        'TM_TOV_PCT_Agg', 'EFG_PCT_Agg', 'TS_PCT_Agg', 'USG_PCT_Agg', 'E_USG_PCT_Agg', 'E_PACE_Agg',
                        'PACE_Agg', 'PACE_PER40_Agg', 'POSS_Agg', 'PIE_Agg', 'Wins', 'Losses', 'Win_Pct', 'is_B2B',
                        'is_B2B_First','is_B2B_Second','Days_Rest_Team', 'Days_Next Game', 'is_Home', 'FGM_Per100_Agg_Opp',
                        'FGA_Per100_Agg_Opp', 'FG_PCT_Agg_Opp', 'FG3M_Per100_Agg_Opp', 'FG3A_Per100_Agg_Opp',
                        'FG3_PCT_Agg_Opp', 'FTM_Per100_Agg_Opp', 'FTA_Per100_Agg_Opp', 'FT_PCT_Agg_Opp', 'OREB_Per100_Agg_Opp',
                        'DREB_Per100_Agg_Opp', 'REB_Per100_Agg_Opp', 'AST_Per100_Agg_Opp', 'STL_Per100_Agg_Opp',
                        'BLK_Per100_Agg_Opp', 'TO_Per100_Agg_Opp', 'PF_Per100_Agg_Opp', 'PTS_Per100_Agg_Opp', 
                        'PLUS_MINUS_Per100_Agg_Opp', 'E_OFF_RATING_Agg_Opp', 'OFF_RATING_Agg_Opp', 'E_DEF_RATING_Agg_Opp',
                        'DEF_RATING_Agg_Opp', 'E_NET_RATING_Agg_Opp', 'NET_RATING_Agg_Opp', 'AST_PCT_Agg_Opp', 'AST_TOV_Agg_Opp',
                        'AST_RATIO_Agg_Opp', 'OREB_PCT_Agg_Opp', 'DREB_PCT_Agg_Opp', 'REB_PCT_Agg_Opp', 'E_TM_TOV_PCT_Agg_Opp',
                        'TM_TOV_PCT_Agg_Opp', 'EFG_PCT_Agg_Opp', 'TS_PCT_Agg_Opp', 'USG_PCT_Agg_Opp', 'E_USG_PCT_Agg_Opp',
                        'E_PACE_Agg_Opp', 'PACE_Agg_Opp', 'PACE_PER40_Agg_Opp', 'POSS_Agg_Opp', 'PIE_Agg_Opp', 'Wins_Opp',
                        'Losses_Opp', 'Win_Pct_Opp', 'is_B2B_Opp', 'is_B2B_First_Opp', 'is_B2B_Second_Opp', 'Days_Rest_Team_Opp',
                        'Days_Next Game_Opp', 'is_Home_Opp']
    stats = stats[cols_of_interest]

    stats_2 = pd.DataFrame()
    stats_2 = stats[['Game_ID', 'Date', 'Team_Opp', 'Team', 'FGM_Per100_Agg_Opp',
                        'FGA_Per100_Agg_Opp', 'FG_PCT_Agg_Opp', 'FG3M_Per100_Agg_Opp', 'FG3A_Per100_Agg_Opp',
                        'FG3_PCT_Agg_Opp', 'FTM_Per100_Agg_Opp', 'FTA_Per100_Agg_Opp', 'FT_PCT_Agg_Opp', 'OREB_Per100_Agg_Opp',
                        'DREB_Per100_Agg_Opp', 'REB_Per100_Agg_Opp', 'AST_Per100_Agg_Opp', 'STL_Per100_Agg_Opp',
                        'BLK_Per100_Agg_Opp', 'TO_Per100_Agg_Opp', 'PF_Per100_Agg_Opp', 'PTS_Per100_Agg_Opp', 
                        'PLUS_MINUS_Per100_Agg_Opp', 'E_OFF_RATING_Agg_Opp', 'OFF_RATING_Agg_Opp', 'E_DEF_RATING_Agg_Opp',
                        'DEF_RATING_Agg_Opp', 'E_NET_RATING_Agg_Opp', 'NET_RATING_Agg_Opp', 'AST_PCT_Agg_Opp', 'AST_TOV_Agg_Opp',
                        'AST_RATIO_Agg_Opp', 'OREB_PCT_Agg_Opp', 'DREB_PCT_Agg_Opp', 'REB_PCT_Agg_Opp', 'E_TM_TOV_PCT_Agg_Opp',
                        'TM_TOV_PCT_Agg_Opp', 'EFG_PCT_Agg_Opp', 'TS_PCT_Agg_Opp', 'USG_PCT_Agg_Opp', 'E_USG_PCT_Agg_Opp',
                        'E_PACE_Agg_Opp', 'PACE_Agg_Opp', 'PACE_PER40_Agg_Opp', 'POSS_Agg_Opp', 'PIE_Agg_Opp', 'Wins_Opp',
                        'Losses_Opp', 'Win_Pct_Opp', 'is_B2B_Opp', 'is_B2B_First_Opp', 'is_B2B_Second_Opp', 'Days_Rest_Team_Opp',
                        'Days_Next Game_Opp', 'is_Home_Opp', 'FGM_Per100_Agg', 'FGA_Per100_Agg', 'FG_PCT_Agg', 
                        'FG3M_Per100_Agg',  'FG3A_Per100_Agg',  'FG3_PCT_Agg', 'FTM_Per100_Agg', 'FTA_Per100_Agg',
                        'FT_PCT_Agg', 'OREB_Per100_Agg', 'DREB_Per100_Agg', 'REB_Per100_Agg', 'AST_Per100_Agg',
                        'STL_Per100_Agg', 'BLK_Per100_Agg', 'TO_Per100_Agg', 'PF_Per100_Agg', 'PTS_Per100_Agg', 
                        'PLUS_MINUS_Per100_Agg', 'E_OFF_RATING_Agg', 'OFF_RATING_Agg', 'E_DEF_RATING_Agg', 
                        'DEF_RATING_Agg', 'E_NET_RATING_Agg', 'NET_RATING_Agg', 'AST_PCT_Agg', 'AST_TOV_Agg', 
                        'AST_RATIO_Agg', 'OREB_PCT_Agg', 'DREB_PCT_Agg', 'REB_PCT_Agg', 'E_TM_TOV_PCT_Agg', 
                        'TM_TOV_PCT_Agg', 'EFG_PCT_Agg', 'TS_PCT_Agg', 'USG_PCT_Agg', 'E_USG_PCT_Agg', 'E_PACE_Agg',
                        'PACE_Agg', 'PACE_PER40_Agg', 'POSS_Agg', 'PIE_Agg', 'Wins', 'Losses', 'Win_Pct', 'is_B2B',
                        'is_B2B_First','is_B2B_Second','Days_Rest_Team', 'Days_Next Game', 'is_Home']]
    stats_2.columns = stats.columns



    final_stats = pd.merge(stats, stats_2, on = 'Game_ID')
    final_stats.columns = ['Game_ID', 'Date', 'Team1', 'Team2', 'Team1_FGM_Per100_Agg', 'Team1_FGA_Per100_Agg', 
                        'Team1_FG_PCT_Agg', 'Team1_FG3M_Per100_Agg', 'Team1_FG3A_Per100_Agg', 'Team1_FG3_PCT_Agg',
                        'Team1_FTM_Per100_Agg', 'Team1_FTA_Per100_Agg', 'Team1_FT_PCT_Agg', 'Team1_OREB_Per100_Agg',
                        'Team1_DREB_Per100_Agg', 'Team1_REB_Per100_Agg', 'Team1_AST_Per100_Agg', 'Team1_STL_Per100_Agg',
                        'Team1_BLK_Per100_Agg', 'Team1_TO_Per100_Agg', 'Team1_PF_Per100_Agg', 'Team1_PTS_Per100_Agg',
                        'Team1_PLUS_MINUS_Per100_Agg', 'Team1_E_OFF_RATING_Agg', 'Team1_OFF_RATING_Agg',
                        'Team1_E_DEF_RATING_Agg', 'Team1_DEF_RATING_Agg', 'Team1_E_NET_RATING_Agg', 'Team1_NET_RATING_Agg',
                        'Team1_AST_PCT_Agg', 'Team1_AST_TOV_Agg', 'Team1_AST_RATIO_Agg', 'Team1_OREB_PCT_Agg',
                        'Team1_DREB_PCT_Agg', 'Team1_REB_PCT_Agg', 'Team1_E_TM_TOV_PCT_Agg', 'Team1_TM_TOV_PCT_Agg',
                        'Team1_EFG_PCT_Agg', 'Team1_TS_PCT_Agg', 'Team1_USG_PCT_Agg', 'Team1_E_USG_PCT_Agg',
                        'Team1_E_PACE_Agg', 'Team1_PACE_Agg', 'Team1_PACE_PER40_Agg', 'Team1_POSS_Agg', 'Team1_PIE_Agg',
                        'Team1_Wins', 'Team1_Losses', 'Team1_Win_Pct', 'Team1_is_B2B', 'Team1_is_B2B_First',
                        'Team1_is_B2B_Second', 'Team1_Days_Rest_Team', 'Team1_Days_Next Game', 'Team1_is_Home',
                        'Team1_FGM_Per100_Agg_Opp', 'Team1_FGA_Per100_Agg_Opp', 'Team1_FG_PCT_Agg_Opp',
                        'Team1_FG3M_Per100_Agg_Opp', 'Team1_FG3A_Per100_Agg_Opp', 'Team1_FG3_PCT_Agg_Opp',
                        'Team1_FTM_Per100_Agg_Opp', 'Team1_FTA_Per100_Agg_Opp', 'Team1_FT_PCT_Agg_Opp',
                        'Team1_OREB_Per100_Agg_Opp', 'Team1_DREB_Per100_Agg_Opp', 'Team1_REB_Per100_Agg_Opp',
                        'Team1_AST_Per100_Agg_Opp', 'Team1_STL_Per100_Agg_Opp', 'Team1_BLK_Per100_Agg_Opp',
                        'Team1_TO_Per100_Agg_Opp', 'Team1_PF_Per100_Agg_Opp', 'Team1_PTS_Per100_Agg_Opp',
                        'Team1_PLUS_MINUS_Per100_Agg_Opp', 'Team1_E_OFF_RATING_Agg_Opp', 'Team1_OFF_RATING_Agg_Opp',
                        'Team1_E_DEF_RATING_Agg_Opp', 'Team1_DEF_RATING_Agg_Opp', 'Team1_E_NET_RATING_Agg_Opp',
                        'Team1_NET_RATING_Agg_Opp', 'Team1_AST_PCT_Agg_Opp', 'Team1_AST_TOV_Agg_Opp',
                        'Team1_AST_RATIO_Agg_Opp', 'Team1_OREB_PCT_Agg_Opp', 'Team1_DREB_PCT_Agg_Opp',
                        'Team1_REB_PCT_Agg_Opp', 'Team1_E_TM_TOV_PCT_Agg_Opp', 'Team1_TM_TOV_PCT_Agg_Opp',
                        'Team1_EFG_PCT_Agg_Opp', 'Team1_TS_PCT_Agg_Opp', 'Team1_USG_PCT_Agg_Opp', 'Team1_E_USG_PCT_Agg_Opp',
                        'Team1_E_PACE_Agg_Opp', 'Team1_PACE_Agg_Opp', 'Team1_PACE_PER40_Agg_Opp', 'Team1_POSS_Agg_Opp',
                        'Team1_PIE_Agg_Opp', 'Team1_Wins_Opp', 'Team1_Losses_Opp', 'Team1_Win_Pct_Opp',
                        'Team1_is_B2B_Opp',  'Team1_is_B2B_First_Opp', 'Team1_is_B2B_Second_Opp',
                        'Team1_Days_Rest_Team_Opp', 'Team1_Days_Next Game_Opp', 'Team1_is_Home_Opp',
                        'drop_1', 'drop_2', 'drop_3', 'Team2_FGM_Per100_Agg', 'Team2_FGA_Per100_Agg',
                        'Team2_FG_PCT_Agg', 'Team2_FG3M_Per100_Agg', 'Team2_FG3A_Per100_Agg', 'Team2_FG3_PCT_Agg',
                        'Team2_FTM_Per100_Agg', 'Team2_FTA_Per100_Agg','Team2_FT_PCT_Agg', 'Team2_OREB_Per100_Agg',
                        'Team2_DREB_Per100_Agg', 'Team2_REB_Per100_Agg', 'Team2_AST_Per100_Agg', 'Team2_STL_Per100_Agg',
                        'Team2_BLK_Per100_Agg', 'Team2_TO_Per100_Agg', 'Team2_PF_Per100_Agg', 'Team2_PTS_Per100_Agg',
                        'Team2_PLUS_MINUS_Per100_Agg', 'Team2_E_OFF_RATING_Agg', 'Team2_OFF_RATING_Agg',
                        'Team2_E_DEF_RATING_Agg', 'Team2_DEF_RATING_Agg', 'Team2_E_NET_RATING_Agg',
                        'Team2_NET_RATING_Agg', 'Team2_AST_PCT_Agg', 'Team2_AST_TOV_Agg', 'Team2_AST_RATIO_Agg',
                        'Team2_OREB_PCT_Agg', 'Team2_DREB_PCT_Agg', 'Team2_REB_PCT_Agg', 'Team2_E_TM_TOV_PCT_Agg',
                        'Team2_TM_TOV_PCT_Agg_y', 'Team2_EFG_PCT_Agg', 'Team2_TS_PCT_Agg', 'Team2_USG_PCT_Agg',
                        'Team2_E_USG_PCT_Agg', 'Team2_E_PACE_Agg', 'Team2_PACE_Agg', 'Team2_PACE_PER40_Agg',
                        'Team2_POSS_Agg', 'Team2_PIE_Agg', 'Team2_Wins', 'Team2_Losses', 'Team2_Win_Pct',
                        'Team2_is_B2B', 'Team2_is_B2B_First', 'Team2_is_B2B_Second', 'Team2_Days_Rest_Team',
                        'Team2_Days_Next Game', 'Team2_is_Home', 'Team2_FGM_Per100_Agg_Opp',
                        'Team2_FGA_Per100_Agg_Opp', 'Team2_FG_PCT_Agg_Opp', 'Team2_FG3M_Per100_Agg_Opp',
                        'Team2_FG3A_Per100_Agg_Opp', 'Team2_FG3_PCT_Agg_Opp', 'Team2_FTM_Per100_Agg_Opp',
                        'Team2_FTA_Per100_Agg_Opp', 'Team2_FT_PCT_Agg_Opp', 'Team2_OREB_Per100_Agg_Opp',
                        'Team2_DREB_Per100_Agg_Opp', 'Team2_REB_Per100_Agg_Opp', 'Team2_AST_Per100_Agg_Opp',
                        'Team2_STL_Per100_Agg_Opp', 'Team2_BLK_Per100_Agg_Opp', 'Team2_TO_Per100_Agg_Opp',
                        'Team2_PF_Per100_Agg_Opp', 'Team2_PTS_Per100_Agg_Opp', 'Team2_PLUS_MINUS_Per100_Agg_Opp',
                        'Team2_E_OFF_RATING_Agg_Opp', 'Team2_OFF_RATING_Agg_Opp', 'Team2_E_DEF_RATING_Agg_Opp',
                        'Team2_DEF_RATING_Agg_Opp', 'Team2_E_NET_RATING_Agg_Opp', 'Team2_NET_RATING_Agg_Opp',
                        'Team2_AST_PCT_Agg_Opp', 'Team2_AST_TOV_Agg_Opp', 'Team2_AST_RATIO_Agg_Opp',
                        'Team2_OREB_PCT_Agg_Opp', 'Team2_DREB_PCT_Agg_Opp', 'Team2_REB_PCT_Agg_Opp',
                        'Team2_E_TM_TOV_PCT_Agg_Opp', 'Team2_TM_TOV_PCT_Agg_Opp', 'Team2_EFG_PCT_Agg_Opp',
                        'Team2_TS_PCT_Agg_Opp', 'Team2_USG_PCT_Agg_Opp', 'Team2_E_USG_PCT_Agg_Opp',
                        'Team2_E_PACE_Agg_Opp', 'Team2_PACE_Agg_Opp', 'Team2_PACE_PER40_Agg_Opp', 'Team2_POSS_Agg_Opp',
                        'Team2_PIE_Agg_Opp', 'Team2_Wins_Opp', 'Team2_Losses_Opp', 'Team2_Win_Pct_Opp',
                        'Team2_is_B2B_Opp', 'Team2_is_B2B_First_Opp', 'Team2_is_B2B_Second_Opp',
                        'Team2_Days_Rest_Team_Opp', 'Team2_Days_Next Game_Opp', 'Team2_is_Home_Opp']
    final_stats.drop(['drop_1', 'drop_2', 'drop_3'], axis = 1, inplace = True)
    final_stats.dropna(inplace = True)
    final_stats.reset_index(drop = True, inplace = True)
    final_stats.to_csv('current_season_data/season_stats.csv')
    return final_stats

def todays_games(odds):
    data = pd.read_csv('current_season_data/season_stats.csv', index_col = 0)
    schedule = pd.read_csv('current_season_data/schedule.csv', header = 0)
    team_map = {
        'Cleveland Cavaliers' : 'Cavaliers',
        'Charlotte Hornets' : 'Hornets',
        'San Antonio Spurs' : 'Spurs',
        'Indiana Pacers' : 'Pacers',
        'Portland Trail Blazers' : 'Trail Blazers',
        'Philadelphia 76ers' : '76ers',
        'Washington Wizards' : 'Wizards',
        'Atlanta Hawks' : 'Hawks',
        'Chicago Bulls' : 'Bulls',
        'Boston Celtics' : 'Celtics',
        'Toronto Raptors' : 'Raptors',
        'New York Knicks' : 'Knicks',
        'Denver Nuggets' : 'Nuggets',
        'Memphis Grizzlies' : 'Grizzlies',
        'Orlando Magic' : 'Magic',
        'Minnesota Timberwolves' : 'Timberwolves',
        'Oklahoma City Thunder' : 'Thunder',
        'Los Angeles Clippers' : 'Clippers',
        'Milwaukee Bucks' : 'Bucks',
        'Detroit Pistons' : 'Pistons',
        'Miami Heat' : 'Heat',
        'Dallas Mavericks' : 'Mavericks',
        'Sacramento Kings' : 'Kings',
        'Utah Jazz' : 'Jazz',
        'New Orleans Pelicans' : 'Pelicans',
        'Phoenix Suns' : 'Suns',
        'Houston Rockets' : 'Rockets',
        'Los Angeles Lakers' : 'Lakers',
        'Brooklyn Nets' : 'Nets',
        'Golden State Warriors' : 'Warriors'
    }
    intermediate = pd.DataFrame()
    for index, row in odds.iterrows():
        home_team = row.Home_Team
        away_team = row.Away_Team
        home_df = data.loc[(data.Team1==home_team) | (data.Team2==home_team)]
        home_df.reset_index(inplace = True, drop = True)
        away_df = data.loc[(data.Team1==away_team) | (data.Team2==away_team)]
        away_df.reset_index(inplace = True, drop = True)
        home_row = home_df.loc[len(home_df)-1, :]
        away_row = away_df.loc[len(away_df)-1,:]
        if home_row.Team1==home_team:
            cols_home = list()
            for index, value in home_row.iteritems():
                if index.startswith('Team1'):
                    cols_home.append(index)
                final_home = home_row[cols_home]
        if home_row.Team2==home_team:
            cols_home = list()
            for index, value in home_row.iteritems():
                if index.startswith('Team2'):
                    cols_home.append(index)
                final_home = home_row[cols_home]
        if away_row.Team1==away_team:
            cols_away = list()
            for index, value in away_row.iteritems():
                if index.startswith('Team1'):
                    cols_away.append(index)
                final_away = away_row[cols_away]
        if away_row.Team2==away_team:
            cols_away = list()
            for index, value in away_row.iteritems():
                if index.startswith('Team2'):
                    cols_away.append(index)
                final_away = away_row[cols_away]
        row_total = final_home.append(final_away)
        row_total['Game_ID'] = 0
        row_total['Date'] = dt.date.today()
        temp_df = pd.DataFrame(columns = list(row_total.index))
        temp_df = temp_df.append(row_total, ignore_index = True)
        temp_df.columns = ['Team1', 'Team1_FGM_Per100_Agg', 'Team1_FGA_Per100_Agg', 'Team1_FG_PCT_Agg', 'Team1_FG3M_Per100_Agg',
                        'Team1_FG3A_Per100_Agg', 'Team1_FG3_PCT_Agg', 'Team1_FTM_Per100_Agg', 'Team1_FTA_Per100_Agg',
                        'Team1_FT_PCT_Agg', 'Team1_OREB_Per100_Agg', 'Team1_DREB_Per100_Agg', 'Team1_REB_Per100_Agg',
                        'Team1_AST_Per100_Agg', 'Team1_STL_Per100_Agg', 'Team1_BLK_Per100_Agg','Team1_TO_Per100_Agg',
                        'Team1_PF_Per100_Agg', 'Team1_PTS_Per100_Agg', 'Team1_PLUS_MINUS_Per100_Agg', 'Team1_E_OFF_RATING_Agg',
                        'Team1_OFF_RATING_Agg', 'Team1_E_DEF_RATING_Agg', 'Team1_DEF_RATING_Agg', 'Team1_E_NET_RATING_Agg',
                        'Team1_NET_RATING_Agg', 'Team1_AST_PCT_Agg', 'Team1_AST_TOV_Agg', 'Team1_AST_RATIO_Agg',
                        'Team1_OREB_PCT_Agg', 'Team1_DREB_PCT_Agg', 'Team1_REB_PCT_Agg', 'Team1_E_TM_TOV_PCT_Agg',
                        'Team1_TM_TOV_PCT_Agg', 'Team1_EFG_PCT_Agg', 'Team1_TS_PCT_Agg', 'Team1_USG_PCT_Agg',
                        'Team1_E_USG_PCT_Agg', 'Team1_E_PACE_Agg', 'Team1_PACE_Agg', 'Team1_PACE_PER40_Agg',
                        'Team1_POSS_Agg', 'Team1_PIE_Agg', 'Team1_Wins', 'Team1_Losses', 'Team1_Win_Pct',
                        'Team1_is_B2B', 'Team1_is_B2B_First', 'Team1_is_B2B_Second', 'Team1_Days_Rest_Team',
                        'Team1_Days_Next Game', 'Team1_is_Home', 'Team1_FGM_Per100_Agg_Opp', 'Team1_FGA_Per100_Agg_Opp',
                        'Team1_FG_PCT_Agg_Opp', 'Team1_FG3M_Per100_Agg_Opp', 'Team1_FG3A_Per100_Agg_Opp', 'Team1_FG3_PCT_Agg_Opp',
                        'Team1_FTM_Per100_Agg_Opp', 'Team1_FTA_Per100_Agg_Opp', 'Team1_FT_PCT_Agg_Opp', 'Team1_OREB_Per100_Agg_Opp',
                        'Team1_DREB_Per100_Agg_Opp', 'Team1_REB_Per100_Agg_Opp', 'Team1_AST_Per100_Agg_Opp', 'Team1_STL_Per100_Agg_Opp',
                        'Team1_BLK_Per100_Agg_Opp', 'Team1_TO_Per100_Agg_Opp', 'Team1_PF_Per100_Agg_Opp', 'Team1_PTS_Per100_Agg_Opp',
                        'Team1_PLUS_MINUS_Per100_Agg_Opp', 'Team1_E_OFF_RATING_Agg_Opp', 'Team1_OFF_RATING_Agg_Opp',
                        'Team1_E_DEF_RATING_Agg_Opp', 'Team1_DEF_RATING_Agg_Opp', 'Team1_E_NET_RATING_Agg_Opp', 'Team1_NET_RATING_Agg_Opp',
                        'Team1_AST_PCT_Agg_Opp', 'Team1_AST_TOV_Agg_Opp', 'Team1_AST_RATIO_Agg_Opp', 'Team1_OREB_PCT_Agg_Opp',
                        'Team1_DREB_PCT_Agg_Opp', 'Team1_REB_PCT_Agg_Opp', 'Team1_E_TM_TOV_PCT_Agg_Opp', 'Team1_TM_TOV_PCT_Agg_Opp',
                        'Team1_EFG_PCT_Agg_Opp', 'Team1_TS_PCT_Agg_Opp', 'Team1_USG_PCT_Agg_Opp', 'Team1_E_USG_PCT_Agg_Opp',
                        'Team1_E_PACE_Agg_Opp', 'Team1_PACE_Agg_Opp', 'Team1_PACE_PER40_Agg_Opp', 'Team1_POSS_Agg_Opp',
                        'Team1_PIE_Agg_Opp', 'Team1_Wins_Opp', 'Team1_Losses_Opp', 'Team1_Win_Pct_Opp', 'Team1_is_B2B_Opp',
                        'Team1_is_B2B_First_Opp', 'Team1_is_B2B_Second_Opp', 'Team1_Days_Rest_Team_Opp', 'Team1_Days_Next Game_Opp',
                        'Team1_is_Home_Opp', 'Team2', 'Team2_FGM_Per100_Agg', 'Team2_FGA_Per100_Agg', 'Team2_FG_PCT_Agg',
                        'Team2_FG3M_Per100_Agg', 'Team2_FG3A_Per100_Agg', 'Team2_FG3_PCT_Agg', 'Team2_FTM_Per100_Agg',
                        'Team2_FTA_Per100_Agg', 'Team2_FT_PCT_Agg', 'Team2_OREB_Per100_Agg', 'Team2_DREB_Per100_Agg',
                        'Team2_REB_Per100_Agg', 'Team2_AST_Per100_Agg', 'Team2_STL_Per100_Agg', 'Team2_BLK_Per100_Agg',
                        'Team2_TO_Per100_Agg', 'Team2_PF_Per100_Agg', 'Team2_PTS_Per100_Agg', 'Team2_PLUS_MINUS_Per100_Agg',
                        'Team2_E_OFF_RATING_Agg', 'Team2_OFF_RATING_Agg', 'Team2_E_DEF_RATING_Agg', 'Team2_DEF_RATING_Agg',
                        'Team2_E_NET_RATING_Agg', 'Team2_NET_RATING_Agg', 'Team2_AST_PCT_Agg', 'Team2_AST_TOV_Agg',
                        'Team2_AST_RATIO_Agg', 'Team2_OREB_PCT_Agg', 'Team2_DREB_PCT_Agg', 'Team2_REB_PCT_Agg',
                        'Team2_E_TM_TOV_PCT_Agg', 'Team2_TM_TOV_PCT_Agg_y', 'Team2_EFG_PCT_Agg', 'Team2_TS_PCT_Agg',
                        'Team2_USG_PCT_Agg', 'Team2_E_USG_PCT_Agg', 'Team2_E_PACE_Agg', 'Team2_PACE_Agg',
                        'Team2_PACE_PER40_Agg', 'Team2_POSS_Agg', 'Team2_PIE_Agg', 'Team2_Wins', 'Team2_Losses',
                        'Team2_Win_Pct', 'Team2_is_B2B', 'Team2_is_B2B_First', 'Team2_is_B2B_Second',
                        'Team2_Days_Rest_Team', 'Team2_Days_Next Game', 'Team2_is_Home', 'Team2_FGM_Per100_Agg_Opp',
                        'Team2_FGA_Per100_Agg_Opp', 'Team2_FG_PCT_Agg_Opp', 'Team2_FG3M_Per100_Agg_Opp', 'Team2_FG3A_Per100_Agg_Opp',
                        'Team2_FG3_PCT_Agg_Opp', 'Team2_FTM_Per100_Agg_Opp', 'Team2_FTA_Per100_Agg_Opp', 'Team2_FT_PCT_Agg_Opp',
                        'Team2_OREB_Per100_Agg_Opp', 'Team2_DREB_Per100_Agg_Opp', 'Team2_REB_Per100_Agg_Opp', 'Team2_AST_Per100_Agg_Opp',
                        'Team2_STL_Per100_Agg_Opp', 'Team2_BLK_Per100_Agg_Opp', 'Team2_TO_Per100_Agg_Opp', 'Team2_PF_Per100_Agg_Opp',
                        'Team2_PTS_Per100_Agg_Opp', 'Team2_PLUS_MINUS_Per100_Agg_Opp', 'Team2_E_OFF_RATING_Agg_Opp',
                        'Team2_OFF_RATING_Agg_Opp', 'Team2_E_DEF_RATING_Agg_Opp', 'Team2_DEF_RATING_Agg_Opp',
                        'Team2_E_NET_RATING_Agg_Opp', 'Team2_NET_RATING_Agg_Opp', 'Team2_AST_PCT_Agg_Opp', 'Team2_AST_TOV_Agg_Opp',
                        'Team2_AST_RATIO_Agg_Opp', 'Team2_OREB_PCT_Agg_Opp', 'Team2_DREB_PCT_Agg_Opp', 'Team2_REB_PCT_Agg_Opp',
                        'Team2_E_TM_TOV_PCT_Agg_Opp', 'Team2_TM_TOV_PCT_Agg_Opp', 'Team2_EFG_PCT_Agg_Opp', 'Team2_TS_PCT_Agg_Opp',
                        'Team2_USG_PCT_Agg_Opp', 'Team2_E_USG_PCT_Agg_Opp', 'Team2_E_PACE_Agg_Opp', 'Team2_PACE_Agg_Opp',
                        'Team2_PACE_PER40_Agg_Opp', 'Team2_POSS_Agg_Opp', 'Team2_PIE_Agg_Opp', 'Team2_Wins_Opp',
                        'Team2_Losses_Opp', 'Team2_Win_Pct_Opp', 'Team2_is_B2B_Opp', 'Team2_is_B2B_First_Opp',
                        'Team2_is_B2B_Second_Opp', 'Team2_Days_Rest_Team_Opp', 'Team2_Days_Next Game_Opp', 'Team2_is_Home_Opp',
                        'Game_ID', 'Date']
        temp_df = temp_df[data.columns]
        intermediate = intermediate.append(temp_df)
    intermediate.reset_index(drop = True, inplace = True)
    final = pd.DataFrame()
    team1_stats = list()
    team2_stats = list()
    for column in intermediate.columns:
        if (column.startswith('Team1')) & (not column.endswith('Opp')):
            team1_stats.append(column)
        if (column.startswith('Team2')) & (not column.endswith('Opp')):
            team2_stats.append(column)
    final['Game_ID'] = intermediate.Game_ID
    final['Date'] = intermediate.Date
    final['Team1'] = intermediate.Team1
    final['Team2'] = intermediate.Team2
    for column in team1_stats:
        if column != 'Team1':
            final[column] = intermediate[column]
    for column in team2_stats:
        if column != 'Team2':
            col_name = 'Team1_' + column[6:] + '_Opp'
            if col_name == 'Team1_TM_TOV_PCT_Agg_y_Opp':
                col_name = 'Team1_TM_TOV_PCT_Agg_Opp'
            final[col_name] = intermediate[column]
    for column in team2_stats:
        if column != 'Team2':
            final[column] = intermediate[column]
    for column in team1_stats:
        if column != 'Team1':
            col_name = 'Team2_' + column[6:] + '_Opp'
            final[col_name] = intermediate[column]
    final['Team1_is_Home'] = 1
    final['Team2_is_Home'] = 0
    final['Team1_is_Home_Opp'] = 0
    final['Team2_is_Home_Opp'] = 1
    final['Team1_is_B2B'] = 0
    final['Team1_is_B2B_Second'] = 0
    final['Team1_is_B2B_First'] = 0
    final['Team1_is_B2B_Opp'] = 0
    final['Team1_is_B2B_Second_Opp'] = 0
    final['Team1_is_B2B_First_Opp'] = 0

    schedule['Date'] = pd.to_datetime(schedule.Date)
    schedule['Home_Team'] = schedule.Home_Team.apply(lambda x: team_map[x])
    schedule['Away_Team'] = schedule.Away_Team.apply(lambda x: team_map[x])

    for index, row in final.iterrows():
        team = row.Team1
        games_played = row.Team1_Wins + row.Team1_Losses
        df_1 = schedule[(schedule.Home_Team==team) | (schedule.Away_Team == team)]
        df_1.reset_index(inplace = True)
        df_1.reset_index(inplace = True)
        df_1.rename(columns = {'level_0': 'Game_Number'}, inplace = True)
        df_1['Game_Number'] = df_1.Game_Number + 1
        row_today = df_1[df_1.Game_Number==(games_played+1)]
        day = row_today.Date.values[0]
        row_prior = df_1[df_1.Game_Number==games_played]
        day_prior = row_prior.Date.values[0]
        row_after = df_1[df_1.Game_Number==(games_played+2)]
        day_after = row_after.Date.values[0]
        final.loc[index, 'Team1_Days_Rest_Team'] = int(day-day_prior)/86400000000000
        final.loc[index, 'Team1_Days_Next Game'] = int(day_after-day)/86400000000000
        if (int(day-day_prior)) == (172800000000000/2):
            final.loc[index, 'Team1_is_B2B'] = 1
            final.loc[index, 'Team1_is_B2B_Second'] = 1
        if (int(day-day_after)) == (-172800000000000/2):
            final.loc[index, 'Team1_is_B2B'] = 1
            final.loc[index, 'Team1_is_B2B_First'] = 1
    
    for index, row in final.iterrows():
        team = row.Team2
        games_played = row.Team2_Wins + row.Team2_Losses
        df_1 = schedule[(schedule.Home_Team==team) | (schedule.Away_Team == team)]
        df_1.reset_index(inplace = True)
        df_1.reset_index(inplace = True)
        df_1.rename(columns = {'level_0': 'Game_Number'}, inplace = True)
        df_1['Game_Number'] = df_1.Game_Number + 1
        row_today = df_1[df_1.Game_Number==(games_played+1)]
        day = row_today.Date.values[0]
        row_prior = df_1[df_1.Game_Number==games_played]
        day_prior = row_prior.Date.values[0]
        row_after = df_1[df_1.Game_Number==(games_played+2)]
        day_after = row_after.Date.values[0]
        final.loc[index, 'Team1_Days_Rest_Team_Opp'] = int(day-day_prior)/86400000000000
        final.loc[index, 'Team1_Days_Next Game_Opp'] = int(day_after-day)/86400000000000
        if (int(day-day_prior)) == (172800000000000/2):
            final.loc[index, 'Team1_is_B2B_Opp'] = 1
            final.loc[index, 'Team1_is_B2B_Second_Opp'] = 1
        if (int(day-day_after)) == (-172800000000000/2):
            final.loc[index, 'Team1_is_B2B_Opp'] = 1
            final.loc[index, 'Team1_is_B2B_First_Opp'] = 1
    final['Team2_is_B2B'] = final.Team1_is_B2B_Opp
    final['Team2_is_B2B_Second'] = final.Team1_is_B2B_Second_Opp
    final['Team2_is_B2B_First'] = final.Team1_is_B2B_First_Opp
    final['Team2_is_B2B_Opp'] = final.Team1_is_B2B
    final['Team2_is_B2B_Second_Opp'] = final.Team1_is_B2B_Second
    final['Team2_is_B2B_First_Opp'] = final.Team1_is_B2B_First
    final['Team2_Days_Rest_Team'] = final.Team1_Days_Rest_Team_Opp
    final['Team2_Days_Next Game'] = final['Team1_Days_Next Game_Opp']
    final['Team2_Days_Rest_Team_Opp'] = final.Team1_Days_Rest_Team
    final['Team2_Days_Next Game_Opp'] = final['Team1_Days_Next Game']
    final.to_csv('current_season_data/todays_stats.csv')
    return final

def calculate_odds(odds):
    if odds<0:
        return (abs(odds)/(abs(odds)+100))*100
    if odds>0:
        return (100/(odds+100))*100

def retrieve_odds(save):
    team_map = {
        'WAS' : 'Wizards',
        'BOS' : 'Celtics',
        'NOP' : 'Pelicans',
        'NYK' : 'Knicks',
        'DET' : 'Pistons',
        'ORL' : 'Magic',
        'PHI' : '76ers',
        'ATL' : 'Hawks',
        'IND' : 'Pacers',
        'TOR' : 'Raptors',
        'MEM' : 'Grizzlies',
        'MIA' : 'Heat',
        'CHI' : 'Bulls',
        'UTA' : 'Jazz',
        'MIL' : 'Bucks',
        'SAS' : 'Spurs',
        'GSW' : 'Warriors',
        'OKC' : 'Thunder',
        'MIN' : 'Timberwolves',
        'DEN' : 'Nuggets',
        'PHX' : 'Suns',
        'CLE' : 'Cavaliers',
        'DAL' : 'Mavericks',
        'SAC' : 'Kings',
        'CHA' : 'Hornets',
        'POR' : 'Trail Blazers',
        'BKN' : 'Nets',
        'LAL' : 'Lakers',
        'LAC' : 'Clippers',
        'HOU' : 'Rockets'
    }
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('https://www.actionnetwork.com/nba/odds')
    ml_button = driver.find_element_by_xpath("//*[@id='__next']/div/main/div/div[3]/div[2]/div[1]/label[3]")
    ml_button.click()
    spread_button = driver.find_element_by_xpath("//*[@id='__next']/div/main/div/div[3]/div[2]/div[1]/label[1]")
    spread_button.click()
    html = driver.page_source
    tables = pd.read_html(html)
    odds = tables[0]
    team_regex = r'[A-Z]{2,3}'
    odds_df = pd.DataFrame(columns = ['Home_Team', 'Away_Team', 'Home_Odds', 'Away_Odds', 'Date'])
    for index, row in odds.iterrows():
        teams = re.findall(team_regex, row.Scheduled)
        teams = teams[1:]
        away_team = teams[0]
        home_team = teams[1]
        ml_string = row['Unnamed: 4']
        if len(ml_string) == 34:
            ml_away = ml_string[11:15]
            ml_home = ml_string[-6:-2]
        if len(ml_string) != 34:
            ml_string = ml_string.replace('Right Arrow', '')
            ml_string = ml_string.replace('ML', '')
            if (ml_string[4] == '+') | (ml_string[4]=='-'):
                ml_away = ml_string[:4]
                ml_home = ml_string[4:]
            else:
                ml_away = ml_string[:5]
                ml_home = ml_string[5:]
        try:
            ml_away = float(ml_away)
        except:
            continue
        try:
            ml_home = float(ml_home)
        except:
            continue
        date = dt.date.today()
        to_append = [home_team, away_team, ml_home, ml_away, date]
        append = pd.Series(to_append, index = odds_df.columns)
        odds_df = odds_df.append(append, ignore_index = True)
    odds_df['Home_Prob'] = odds_df.Home_Odds.apply(calculate_odds)
    odds_df['Away_Prob'] = odds_df.Away_Odds.apply(calculate_odds)
    odds_df['Home_Team'] = odds_df.Home_Team.apply(lambda x: team_map[x])
    odds_df['Away_Team'] = odds_df.Away_Team.apply(lambda x: team_map[x])
    if save:
        odds_df.to_csv('current_season_data/yesterday_odds.csv')
    return odds_df

def calculate_bets(todays_capital, ml_param, ml_param_underdog, small_advantage, kelly):
    prob_output = pd.read_csv('current_season_data/todays_stats.csv', index_col = 0)
    odds = pd.read_csv('current_season_data/yesterday_odds.csv')
    def kelly_criterion(row):
        if row['Team1_Prob_Diff'] < 0:
            return 0
        else:
            p = row['Team1_Prob']
            q = 1-p
            ml = row['Home_Odds']
            if ml>=0:
                b = (ml/100)
            if ml<0:
                b = (100/abs(ml))
            kc = ((p*b) - q) / b
            if (kc > 0.5) & (kc<0.6):
                return kc/(kelly+2)
            if (kc > 0.6) & (kc<0.7):
                return kc/(kelly+4)
            if kc > 0.7:
                return kc/(kelly+7)
            else:
                return kc/kelly
    def kelly_criterion_2(row):
        if row['Team2_Prob_Diff'] < 0:
            return 0
        else:
            p = row['Team2_Prob']
            q = 1-p
            ml = row['Away_Odds']
            if ml>=0:
                b = (ml/100)
            if ml<0:
                b = (100/abs(ml))
            kc = ((p*b) - q) / b
            if (kc > 0.5) & (kc<0.6):
                return kc/(kelly+2)
            if (kc > 0.6) & (kc<0.7):
                return kc/(kelly+4)
            if kc > 0.7:
                return kc/(kelly+7)
            else:
                return kc/kelly
    odds = odds[['Home_Team', 'Home_Odds', 'Away_Odds', 'Home_Prob', 'Away_Prob']]
    merged = pd.merge(prob_output, odds, left_on = 'Team1', right_on = 'Home_Team')
    merged.drop(['Home_Team', 'X'], axis = 1, inplace = True)
    merged['Team2_Prob'] = 1-merged.Team1_Prob
    merged['Team1_Prob_Diff'] = merged.Team1_Prob - merged.Home_Prob/100
    merged['Team2_Prob_Diff'] = merged.Team2_Prob - merged.Away_Prob/100
    merged['Team1_KC'] = merged.apply(kelly_criterion, axis = 1)
    merged['Team2_KC'] = merged.apply(kelly_criterion_2, axis = 1)
    merged['Team1_Bet'] = 0
    merged['Team2_Bet'] = 0
    merged['Team1_Payoff'] = 0
    merged['Team2_Payoff'] = 0
    for index, row in merged.iterrows():
        if (row.Team1_KC == 0) & (row.Team2_KC == 0):
            merged.loc[index, 'Team1_Bet'] = 0
            merged.loc[index, 'Team2_Bet'] = 0
            continue
        if ((row.Team1_Prob_Diff<0) & (row.Team2_Prob_Diff<small_advantage)) | ((row.Team1_Prob_Diff<small_advantage) & (row.Team2_Prob_Diff<0)):
            merged.loc[index, 'Team1_Bet'] = 0
            merged.loc[index, 'Team2_Bet'] = 0
            continue
            
        if row.Team1_KC>0:
            merged.loc[index, 'Team1_Bet'] = todays_capital*row.Team1_KC
        if row.Team2_KC>0:
            merged.loc[index, 'Team2_Bet'] = todays_capital*row.Team2_KC
        
        if merged.loc[index, 'Team1_Bet']>0:
            if row.Home_Odds<0:
                merged.loc[index, 'Team1_Payoff'] = (merged.loc[index, 'Team1_Bet']/abs(row.Home_Odds))*100
            if row.Home_Odds>0:
                merged.loc[index, 'Team1_Payoff'] = merged.loc[index, 'Team1_Bet'] * (row.Home_Odds/100)
        if merged.loc[index, 'Team2_Bet']>0:
            if row.Away_Odds<0:
                merged.loc[index, 'Team2_Payoff'] = (merged.loc[index, 'Team2_Bet']/abs(row.Away_Odds))*100
            if row.Away_Odds>0:
                merged.loc[index, 'Team2_Payoff'] = merged.loc[index, 'Team2_Bet'] * (row.Away_Odds/100)
        
        if (merged.loc[index, 'Team1_Bet']>0) & (row.Home_Odds<ml_param):
            merged.loc[index, 'Team1_Bet'] = 0
            merged.loc[index, 'Team1_Payoff'] = 0
            continue
        if (merged.loc[index, 'Team2_Bet']>0) & (row.Away_Odds<ml_param):
            merged.loc[index, 'Team2_Bet'] = 0
            merged.loc[index, 'Team2_Payoff'] = 0
            continue
        if (merged.loc[index, 'Team1_Bet']>0) & (row.Home_Odds>ml_param_underdog):
            merged.loc[index, 'Team1_Bet'] = 0
            merged.loc[index, 'Team1_Payoff'] = 0
            continue
        if (merged.loc[index, 'Team2_Bet']>0) & (row.Away_Odds>ml_param_underdog):
            merged.loc[index, 'Team2_Bet'] = 0
            merged.loc[index, 'Team2_Payoff'] = 0
            continue
    merged.to_csv('current_season_data/bets.csv')
    return merged

def calculate_bet_results(yesterdays_capital):
    yesterdays_bets = pd.read_csv('current_season_data/bets.csv', index_col = 0)
    formatted_data = pd.read_csv('current_season_data/formatted_data_1.csv', index_col = 0)

    yesterday = dt.date.today() - dt.timedelta(days = 1)
    yesterday = str(yesterday)
    yesterdays_games = formatted_data[formatted_data.Date==yesterday]

    yesterdays_winners = list()
    for index, row in yesterdays_games.iterrows():
        if row.PTS>row.PTS_Opp:
            yesterdays_winners.append(row.Team)
        else:
            yesterdays_winners.append(row.Team_Opp)
    
    results = pd.DataFrame()
    yesterdays_bets['Won_Bet'] = 0
    yesterdays_bets['Money_Tracker'] = 0
    for index, row in yesterdays_bets.iterrows():
        if (row.Team1_Bet<=0) & (row.Team2_Bet<=0):
            yesterdays_bets.loc[index, 'Won_Bet'] = -1
        if row.Team1_Bet>0:
            if row.Team1 in yesterdays_winners:
                yesterdays_bets.loc[index, 'Won_Bet'] = 1
        if row.Team2_Bet>0:
            if row.Team2 in yesterdays_winners:
                yesterdays_bets.loc[index, 'Won_Bet'] = 1
        
        if index==0:
            if yesterdays_bets.loc[index, 'Won_Bet']==1:
                yesterdays_bets.loc[index, 'Money_Tracker'] = yesterdays_capital + row.Team1_Payoff + row.Team2_Payoff
            else:
                yesterdays_bets.loc[index, 'Money_Tracker'] = yesterdays_capital - row.Team1_Bet - row.Team2_Bet
        else:
            if yesterdays_bets.loc[index, 'Won_Bet']==1:
                yesterdays_bets.loc[index, 'Money_Tracker'] = yesterdays_bets.loc[(index-1), 'Money_Tracker'] + row.Team1_Payoff + row.Team2_Payoff
            else:
                yesterdays_bets.loc[index, 'Money_Tracker'] = yesterdays_bets.loc[(index-1), 'Money_Tracker'] - row.Team1_Bet - row.Team2_Bet
            
    string = f"Today's capital is {yesterdays_bets.loc[len(yesterdays_bets)-1, 'Money_Tracker']}"
    print(string)

    # yesterdays_bets.to_csv('current_season_data/results_tracker.csv')
    old_results = pd.read_csv('current_season_data/results_tracker.csv', index_col = 0)
    results = old_results.append(yesterdays_bets)
    results.to_csv('current_season_data/results_tracker.csv')
    return

def calculate_bets_external(todays_capital_538, todays_capital_combined, ml_param, ml_param_underdog, small_advantage):
    
    def kc(row, Home):
        if Home:
            diff = row.Home_Prob - row.Home_Prob_Implied
            if diff < 0:
                return 0
            else:
                p = row.Home_Prob
                q = 1-p
                ml = row.Home_Odds
                if ml>=0:
                    b = (ml/100)
                if ml<0:
                    b = (100/abs(ml))
                kc = ((p*b) - q) / b
                return (kc/8.0)
        else:
            diff_away = row.Away_Prob - row.Away_Prob_Implied
            if diff_away < 0:
                return 0
            else:
                p = row.Away_Prob
                q = 1-p
                ml = row.Away_Odds
                if ml>=0:
                    b = (ml/100)
                if ml<0:
                    b = (100/abs(ml))
                kc = ((p*b) - q) / b
                return (kc/8.0)

    def kc_combined(row, Home):
        if Home:
            diff = row.Home_Prob_Combined - row.Home_Prob_Implied
            if diff < 0:
                return 0
            else:
                p = row.Home_Prob_Combined
                q = 1-p
                ml = row.Home_Odds
                if ml>=0:
                    b = (ml/100)
                if ml<0:
                    b = (100/abs(ml))
                kc = ((p*b) - q) / b
                return (kc/8.0)
        else:
            diff_away = row.Away_Prob_Combined - row.Away_Prob_Implied
            if diff_away < 0:
                return 0
            else:
                p = row.Away_Prob_Combined
                q = 1-p
                ml = row.Away_Odds
                if ml>=0:
                    b = (ml/100)
                if ml<0:
                    b = (100/abs(ml))
                kc = ((p*b) - q) / b
                return (kc/8.0)
    
    tables = pd.read_html('https://projects.fivethirtyeight.com/2022-nba-predictions/games/')
    fivethirtyeight_data = pd.DataFrame(columns = ['Date', 'Away_Team', 'Away_Prob', 'Home_Team', 'Home_Prob'])
    for i, table in enumerate(tables):
        if i == 0:
            continue
        if i > 30:
            break
        if i % 2 == 0:
            matchup_data = table.iloc[:, [2,4]]
            matchup_data.drop(2, axis = 0, inplace = True)
            matchup_data.columns = ['Teams', 'Probability']
            away_team = matchup_data.loc[0, 'Teams']
            away_prob = matchup_data.loc[0, 'Probability']
            home_team = matchup_data.loc[1, 'Teams']
            home_prob = matchup_data.loc[1, 'Probability']
            date = dt.date.today()
            data_series = pd.Series([date, away_team, away_prob, home_team, home_prob], index = fivethirtyeight_data.columns)
            fivethirtyeight_data = fivethirtyeight_data.append(data_series, ignore_index = True)
    odds = pd.read_csv('current_season_data/yesterday_odds.csv', index_col = 0)
    merged = pd.merge(fivethirtyeight_data, odds, on = ['Home_Team', 'Away_Team'])
    merged.columns = ['Date', 'Away_Team', 'Away_Prob', 'Home_Team', 'Home_Prob', 'Home_Odds', 'Away_Odds', 
                    'drop', 'Home_Prob_Implied', 'Away_Prob_Implied']
    merged.drop(['drop'], axis = 1, inplace = True)
    merged['Away_Prob'] = merged.Away_Prob.str.strip('%')
    merged['Away_Prob'] = merged.Away_Prob.astype(float)
    merged['Away_Prob'] = merged.Away_Prob/100
    merged['Home_Prob'] = merged.Home_Prob.str.strip('%')
    merged['Home_Prob'] = merged.Home_Prob.astype(float)
    merged['Home_Prob'] = merged.Home_Prob/100
    merged['Home_Prob_Implied'] = merged.Home_Prob_Implied/100
    merged['Away_Prob_Implied'] = merged.Away_Prob_Implied/100
    merged['Home_KC'] = merged.apply(kc, axis = 1, Home = True)
    merged['Away_KC'] = merged.apply(kc, axis = 1, Home = False)
    merged['Home_Bet'] = 0
    merged['Away_Bet'] = 0
    merged['Home_Payoff'] = 0
    merged['Away_Payoff'] = 0

    for index, row in merged.iterrows():
        if (row.Home_KC == 0) & (row.Away_KC == 0):
            merged.loc[index, 'Home_Bet'] = 0
            merged.loc[index, 'Away_Bet'] = 0
            continue
        if (((row.Home_Prob - row.Home_Prob_Implied)<0) & ((row.Away_Prob - row.Away_Prob_Implied)<small_advantage)) | (((row.Home_Prob - row.Home_Prob_Implied)<small_advantage) & ((row.Away_Prob - row.Away_Prob_Implied)<0)):
            merged.loc[index, 'Home_Bet'] = 0
            merged.loc[index, 'Away_Bet'] = 0
            continue
            
        if row.Home_KC>0:
            merged.loc[index, 'Home_Bet'] = todays_capital_538*row.Home_KC
        if row.Away_KC>0:
            merged.loc[index, 'Away_Bet'] = todays_capital_538*row.Away_KC
            
        if merged.loc[index, 'Home_Bet']>0:
            if row.Home_Odds<0:
                merged.loc[index, 'Home_Payoff'] = (merged.loc[index, 'Home_Bet']/abs(row.Home_Odds))*100
            if row.Home_Odds>0:
                merged.loc[index, 'Home_Payoff'] = merged.loc[index, 'Home_Bet'] * (row.Home_Odds/100)
        if merged.loc[index, 'Away_Bet']>0:
            if row.Away_Odds<0:
                merged.loc[index, 'Away_Payoff'] = (merged.loc[index, 'Away_Bet']/abs(row.Away_Odds))*100
            if row.Away_Odds>0:
                merged.loc[index, 'Away_Payoff'] = merged.loc[index, 'Away_Bet'] * (row.Away_Odds/100)

        if (merged.loc[index, 'Home_Bet']>0) & (row.Home_Odds<ml_param):
            merged.loc[index, 'Home_Bet'] = 0
            merged.loc[index, 'Home_Payoff'] = 0
            continue
        if (merged.loc[index, 'Away_Bet']>0) & (row.Away_Odds<ml_param):
            merged.loc[index, 'Away_Bet'] = 0
            merged.loc[index, 'Away_Payoff'] = 0
            continue
        if (merged.loc[index, 'Home_Bet']>0) & (row.Home_Odds>ml_param_underdog):
            merged.loc[index, 'Home_Bet'] = 0
            merged.loc[index, 'Home_Payoff'] = 0
            continue
        if (merged.loc[index, 'Away_Bet']>0) & (row.Away_Odds>ml_param_underdog):
            merged.loc[index, 'Away_Bet'] = 0
            merged.loc[index, 'Away_Payoff'] = 0
            continue
    

    bets = pd.read_csv('current_season_data/bets.csv', index_col = 0)
    bets_small = bets[['Team1', 'Team2', 'Team1_Prob', 'Team2_Prob']]
    merged_2 = pd.merge(merged, bets_small, left_on = ['Home_Team', 'Away_Team'], right_on = ['Team1', 'Team2'])
    merged_2.drop(['Team1', 'Team2'], axis = 1, inplace = True)
    merged_2.columns
    merged_2.columns = ['Date', 'Away_Team', 'Away_Prob_538', 'Home_Team', 'Home_Prob_538', 'Home_Odds',
        'Away_Odds', 'Home_Prob_Implied', 'Away_Prob_Implied', 'Home_KC',
        'Away_KC', 'Home_Bet', 'Away_Bet', 'Home_Payoff', 'Away_Payoff',
        'Home_Prob_Prop', 'Away_Prob_Prop']
    merged_2['Home_Prob_Combined'] = (merged_2.Home_Prob_538 + merged_2.Home_Prob_Prop)/2
    merged_2['Away_Prob_Combined'] = (merged_2.Away_Prob_538 + merged_2.Away_Prob_Prop)/2
    merged_2['Home_KC_Combined'] = merged_2.apply(kc_combined, axis = 1, Home = True)
    merged_2['Away_KC_Combined'] = merged_2.apply(kc_combined, axis = 1, Home = False)
    merged_2['Home_Bet_Combined'] = 0
    merged_2['Away_Bet_Combined'] = 0
    merged_2['Home_Payoff_Combined'] = 0
    merged_2['Away_Payoff_Combined'] = 0
    for index, row in merged_2.iterrows():
        if (row.Home_KC_Combined == 0) & (row.Away_KC_Combined == 0):
            merged_2.loc[index, 'Home_Bet_Combined'] = 0
            merged_2.loc[index, 'Away_Bet_Combined'] = 0
            continue
        if (((row.Home_Prob_Combined - row.Home_Prob_Implied)<0) & ((row.Away_Prob_Combined - row.Away_Prob_Implied)<small_advantage)) | (((row.Home_Prob_Combined - row.Home_Prob_Implied)<small_advantage) & ((row.Away_Prob_Combined - row.Away_Prob_Implied)<0)):
            merged_2.loc[index, 'Home_Bet_Combined'] = 0
            merged_2.loc[index, 'Away_Bet_Combined'] = 0
            continue
            
        if row.Home_KC_Combined>0:
            merged_2.loc[index, 'Home_Bet_Combined'] = todays_capital_combined*row.Home_KC_Combined
        if row.Away_KC_Combined>0:
            merged_2.loc[index, 'Away_Bet_Combined'] = todays_capital_combined*row.Away_KC_Combined
            
        if merged_2.loc[index, 'Home_Bet_Combined']>0:
            if row.Home_Odds<0:
                merged_2.loc[index, 'Home_Payoff_Combined'] = (merged_2.loc[index, 'Home_Bet_Combined']/abs(row.Home_Odds))*100
            if row.Home_Odds>0:
                merged_2.loc[index, 'Home_Payoff_Combined'] = merged_2.loc[index, 'Home_Bet_Combined'] * (row.Home_Odds/100)
        if merged_2.loc[index, 'Away_Bet_Combined']>0:
            if row.Away_Odds<0:
                merged_2.loc[index, 'Away_Payoff_Combined'] = (merged_2.loc[index, 'Away_Bet_Combined']/abs(row.Away_Odds))*100
            if row.Away_Odds>0:
                merged_2.loc[index, 'Away_Payoff_Combined'] = merged_2.loc[index, 'Away_Bet_Combined'] * (row.Away_Odds/100)

        if (merged_2.loc[index, 'Home_Bet_Combined']>0) & (row.Home_Odds<ml_param):
            merged_2.loc[index, 'Home_Bet_Combined'] = 0
            merged_2.loc[index, 'Home_Payoff_Combined'] = 0
            continue
        if (merged_2.loc[index, 'Away_Bet_Combined']>0) & (row.Away_Odds<ml_param):
            merged_2.loc[index, 'Away_Bet_Combined'] = 0
            merged_2.loc[index, 'Away_Payoff_Combined'] = 0
            continue
        if (merged_2.loc[index, 'Home_Bet_Combined']>0) & (row.Home_Odds>ml_param_underdog):
            merged_2.loc[index, 'Home_Bet_Combined'] = 0
            merged_2.loc[index, 'Home_Payoff_Combined'] = 0
            continue
        if (merged_2.loc[index, 'Away_Bet_Combined']>0) & (row.Away_Odds>ml_param_underdog):
            merged_2.loc[index, 'Away_Bet_Combined'] = 0
            merged_2.loc[index, 'Away_Payoff_Combined'] = 0
            continue
    merged_2.to_csv('current_season_data/bets_external.csv')
    return

def calculate_bet_results_external(yesterdays_capital_538, yesterdays_capital_combined):
    yesterdays_bets = pd.read_csv('current_season_data/bets_external.csv', index_col = 0)
    formatted_data = pd.read_csv('current_season_data/formatted_data_1.csv', index_col = 0)
    yesterday = dt.date.today() - dt.timedelta(days = 1)
    yesterday = str(yesterday)
    yesterdays_games = formatted_data[formatted_data.Date==yesterday]
    yesterdays_winners = list()
    for index, row in yesterdays_games.iterrows():
        if row.PTS>row.PTS_Opp:
            yesterdays_winners.append(row.Team)
        else:
            yesterdays_winners.append(row.Team_Opp)
    results = pd.DataFrame()
    yesterdays_bets['Won_Bet_538'] = 0
    yesterdays_bets['Money_Tracker_538'] = 0
    yesterdays_bets['Won_Bet_Combined'] = 0
    yesterdays_bets['Money_Tracker_Combined'] = 0
    for index, row in yesterdays_bets.iterrows():
        if (row.Home_Bet<=0) & (row.Away_Bet<=0):
            yesterdays_bets.loc[index, 'Won_Bet_538'] = -1
        if row.Home_Bet>0:
            if row.Home_Team in yesterdays_winners:
                yesterdays_bets.loc[index, 'Won_Bet_538'] = 1
        if row.Away_Bet>0:
            if row.Away_Team in yesterdays_winners:
                yesterdays_bets.loc[index, 'Won_Bet_538'] = 1
        if index==0:
            if yesterdays_bets.loc[index, 'Won_Bet_538']==1:
                yesterdays_bets.loc[index, 'Money_Tracker_538'] = yesterdays_capital_538 + row.Home_Payoff + row.Away_Payoff
            else:
                yesterdays_bets.loc[index, 'Money_Tracker_538'] = yesterdays_capital_538 - row.Home_Bet - row.Away_Bet
        else:
            if yesterdays_bets.loc[index, 'Won_Bet_538']==1:
                yesterdays_bets.loc[index, 'Money_Tracker_538'] = yesterdays_bets.loc[(index-1), 'Money_Tracker_538'] + row.Home_Payoff + row.Away_Payoff
            else:
                yesterdays_bets.loc[index, 'Money_Tracker_538'] = yesterdays_bets.loc[(index-1), 'Money_Tracker_538'] - row.Home_Bet - row.Away_Bet

    for index, row in yesterdays_bets.iterrows():
        if (row.Home_Bet_Combined<=0) & (row.Away_Bet_Combined<=0):
            yesterdays_bets.loc[index, 'Won_Bet_Combined'] = -1
        if row.Home_Bet_Combined>0:
            if row.Home_Team in yesterdays_winners:
                yesterdays_bets.loc[index, 'Won_Bet_Combined'] = 1
        if row.Away_Bet_Combined>0:
            if row.Away_Team in yesterdays_winners:
                yesterdays_bets.loc[index, 'Won_Bet_Combined'] = 1
        if index==0:
            if yesterdays_bets.loc[index, 'Won_Bet_Combined']==1:
                yesterdays_bets.loc[index, 'Money_Tracker_Combined'] = yesterdays_capital_combined + row.Home_Payoff_Combined + row.Away_Payoff_Combined
            else:
                yesterdays_bets.loc[index, 'Money_Tracker_Combined'] = yesterdays_capital_combined - row.Home_Bet_Combined - row.Away_Bet_Combined
        else:
            if yesterdays_bets.loc[index, 'Won_Bet_Combined']==1:
                yesterdays_bets.loc[index, 'Money_Tracker_Combined'] = yesterdays_bets.loc[(index-1), 'Money_Tracker_Combined'] + row.Home_Payoff_Combined + row.Away_Payoff_Combined
            else:
                yesterdays_bets.loc[index, 'Money_Tracker_Combined'] = yesterdays_bets.loc[(index-1), 'Money_Tracker_Combined'] - row.Home_Bet_Combined - row.Away_Bet_Combined

    string = f"Today's 538 capital is {yesterdays_bets.loc[len(yesterdays_bets)-1, 'Money_Tracker_538']}"
    print(string)

    string = f"Today's combined capital is {yesterdays_bets.loc[len(yesterdays_bets)-1, 'Money_Tracker_Combined']}"
    print(string)

    old_results = pd.read_csv('current_season_data/results_tracker_external.csv', index_col = 0)
    results = old_results.append(yesterdays_bets)
    results.to_csv('current_season_data/results_tracker_external.csv')
    return
