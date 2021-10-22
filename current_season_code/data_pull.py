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
        games_df_2021 = pd.read_csv('current_season_data/api_data_' + str(year) + '_advanced.csv', index_col = 0)
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
        games_df_2021 = pd.read_csv('current_season_data/api_data_' + str(year) + '_traditional.csv', index_col = 0)
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
        'E_USG_PCT', 'E_PACE', 'PACE', 'PACE_PER40', 'POSS', 'PIE']
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
    #teams += ['Hawks']
    for team in teams:
        record_dict[team + '_wins'] = 0.0
        record_dict[team + '_losses'] = 0.0
    for index, row in final.iterrows():
        final.loc[index, 'Team_1_wins'] = record_dict[row.TEAM_NAME_x + "_wins"]
        final.loc[index, 'Team_1_losses'] = record_dict[row.TEAM_NAME_x + "_losses"]
        final.loc[index, 'Team_2_wins'] = record_dict[row.TEAM_NAME_y + "_wins"]
        final.loc[index, 'Team_2_losses'] = record_dict[row.TEAM_NAME_y + "_losses"]
        if row.PTS_x>row.PTS_y:
            record_dict[row.TEAM_NAME_x + "_wins"] += 1.0
            record_dict[row.TEAM_NAME_y + "_losses"] += 1.0
        if row.PTS_x<row.PTS_y:
            record_dict[row.TEAM_NAME_x + "_losses"] += 1.0
            record_dict[row.TEAM_NAME_y + "_wins"] += 1.0
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
        'E_USG_PCT_x', 'E_PACE_x', 'PACE_x', 'PACE_PER40_x', 'POSS_x', 'PIE_x',
        'GAME_ID_y', 'TEAM_ID_y', 'FGM_y', 'FGA_y', 'FG_PCT_y',
        'FG3M_y', 'FG3A_y', 'FG3_PCT_y', 'FTM_y', 'FTA_y', 'FT_PCT_y', 'OREB_y',
        'DREB_y', 'REB_y', 'AST_y', 'STL_y', 'BLK_y', 'TO_y', 'PF_y', 'PTS_y',
        'PLUS_MINUS_y', 'E_OFF_RATING_y', 'OFF_RATING_y', 'E_DEF_RATING_y',
        'DEF_RATING_y', 'E_NET_RATING_y', 'NET_RATING_y', 'AST_PCT_y',
        'AST_TOV_y', 'AST_RATIO_y', 'OREB_PCT_y', 'DREB_PCT_y', 'REB_PCT_y',
        'E_TM_TOV_PCT_y', 'TM_TOV_PCT_y', 'EFG_PCT_y', 'TS_PCT_y', 'USG_PCT_y',
        'E_USG_PCT_y', 'E_PACE_y', 'PACE_y', 'PACE_PER40_y', 'POSS_y', 'PIE_y',
        'Team_1_wins', 'Team_1_losses', 'Team_2_wins', 'Team_2_losses',
        'Team_1_win_pct', 'Team_2_win_pct']]

    print(final.shape)
    return final