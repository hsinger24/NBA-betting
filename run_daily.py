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
from current_season_code.functions import *

##########NECESSARY VARIABLES##########

year = 2021
continue_value_advanced = 366
continue_value_traditional = 366
ml_param = -1750
ml_param_underdog = 1000
small_advantage = .025
kelly = 12

##########RUN##########

results = pd.read_csv('current_season_data/results_tracker.csv')
capital = results.loc[len(results)-1, 'Money_Tracker']
results_external = pd.read_csv('current_season_data/results_tracker_external.csv')
capital_538 = results_external.loc[len(results_external)-1, 'Money_Tracker_538']
capital_combined = results_external.loc[len(results_external)-1, 'Money_Tracker_Combined']

retrieve_advanced_stats(year = year, continue_value=continue_value_advanced)
retrieve_traditional_stats(year = year, continue_value=continue_value_traditional)
formatted_api_data = format_api_data(year = year)
formatted_data_1(formatted_api_data)
final_stats = formatted_data_2()
odds = retrieve_odds(save = True)
todays_games(odds)
calculate_bet_results(capital)
calculate_bet_results_external(yesterdays_capital_538 = capital_538, yesterdays_capital_combined = capital_combined)

########## RUN THE R FILE ##########

# results = pd.read_csv('current_season_data/results_tracker.csv')
# capital = results.loc[len(results)-1, 'Money_Tracker']
# results_external = pd.read_csv('current_season_data/results_tracker_external.csv')
# capital_538 = results_external.loc[len(results_external)-1, 'Money_Tracker_538']
# capital_combined = results_external.loc[len(results_external)-1, 'Money_Tracker_Combined']

# calculate_bets(todays_capital = capital, ml_param = ml_param, ml_param_underdog = ml_param_underdog, small_advantage = small_advantage, kelly = kelly)
# calculate_bets_external(todays_capital_538 = capital_538, todays_capital_combined = capital_combined, ml_param = ml_param, ml_param_underdog = ml_param_underdog, small_advantage = small_advantage) 

