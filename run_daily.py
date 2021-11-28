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

todays_capital = 89085
yesterdays_capital = 89085
year = 2021
continue_value_advanced = 300
continue_value_traditional = 300
ml_param = -1750
ml_param_underdog = 1000
small_advantage = .025
kelly = 12

##########RUN##########

retrieve_advanced_stats(year = year, continue_value=continue_value_advanced)
retrieve_traditional_stats(year = year, continue_value=continue_value_traditional)
formatted_api_data = format_api_data(year = year)
formatted_data_1(formatted_api_data)
final_stats = formatted_data_2()
odds = retrieve_odds(save = True)
todays_games(odds)
calculate_bet_results(yesterdays_capital)

########## RUN THE R FILE ##########

# calculate_bets(todays_capital = todays_capital, ml_param = ml_param, ml_param_underdog = ml_param_underdog, small_advantage = small_advantage, kelly = kelly)
