##########IMPORTS##########

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import re
import json
import unidecode
import re
import datetime as dt
from current_season_code.data_pull import *

##########NECESSARY VARIABLES##########

year = 2021
continue_value_advanced = 17
continue_value_traditional = 17

##########FUNCTIONS##########

def calculate_odds(odds):
    if odds<0:
        return (abs(odds)/(abs(odds)+100))*100
    if odds>0:
        return (100/(odds+100))*100

def retrieve_odds():
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
    odds_df = pd.DataFrame(columns = ['Home_Team', 'Away_Team', 'Home_Odds', 'Away_Odds'])
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
        to_append = [home_team, away_team, ml_home, ml_away]
        append = pd.Series(to_append, index = odds_df.columns)
        odds_df = odds_df.append(append, ignore_index = True)
    odds_df['Home_Prob'] = odds_df.Home_Odds.apply(calculate_odds)
    odds_df['Away_Prob'] = odds_df.Away_Odds.apply(calculate_odds)
    return odds_df

##########RUN##########

odds = retrieve_odds()
retrieve_advanced_stats(year = year, continue_value=continue_value_advanced)
retrieve_traditional_stats(year = year, continue_value=continue_value_traditional)
formatted_api_data = format_api_data(year = year)

