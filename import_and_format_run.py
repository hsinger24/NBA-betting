from formatting_data import *
from importing_data import *
import pandas as pd

year = 2018
# Run if we need to call API to get data and save to Data folder

# retrieve_advanced_stats(year = year, continue_value = None)
# retrieve_traditional_stats(year = year, continue_value = None)

# Run to format data and save year's final dataframe to Data folder

formatted_api_data = format_api_data(year)
formatted_odds = retrieve_and_format_odds(year, formatted_api_data)
almost_final = format_merged(year = year, formatted_odds = formatted_odds, formatted_api_data = formatted_api_data)
#almost_final = pd.read_csv('data/final_stats_' + str(year) + '.csv', index_col = 0)
print(almost_final.shape)
format_final_stats(year, almost_final, formatted_odds)