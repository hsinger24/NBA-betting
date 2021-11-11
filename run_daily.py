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
continue_value_advanced = 171
continue_value_traditional = 171

##########RUN##########

# retrieve_advanced_stats(year = year, continue_value=continue_value_advanced)
# retrieve_traditional_stats(year = year, continue_value=continue_value_traditional)
# formatted_api_data = format_api_data(year = year)
# formatted_data_1(formatted_api_data)
# final_stats = formatted_data_2()
odds = retrieve_odds(save = True)
todays_games(odds)