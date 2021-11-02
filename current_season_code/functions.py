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
            box_df['Date'] = dt.date.today() - dt.timedelta(days = 1)
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

    print(final.shape)
    return final

def formatted_data_1(formatted_api_data):
    existing_data = pd.read_csv('current_season_data/formatted_data_1.csv')
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
    odds_yesterday = pd.read_csv('current_season_data/yesterday_odds.csv', index_col = 0)
    odds_yesterday['GAME_ID'] = 0
    odds_yesterday
    yesterday = dt.date.today() - dt.timedelta(days = 1)
    yesterday = str(yesterday)
    yesterday_formatted = data[data.Date==yesterday]
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
    final = existing_data.append(merged)
    final.to_csv('current_season_data/formatted_data_1.csv')
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
        ml_away = ml_string[11:15]
        ml_home = ml_string[-6:-2]
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