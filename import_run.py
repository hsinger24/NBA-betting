from formatting_data import *
from importing_data import *

year = 
# Run if we need to call API to get data and save to Data folder

retrieve_advanced_stats(year = year, continue_value = None)
retrieve_traditional_stats(year = year, continue_value = None)

# Run to format data and save year's final dataframe to Data folder

formatted_api_data = format_api_data(year = year)
formatted_odds = retrieve_and_format_odds(year = year)
format_final(year = year, formatted_odds = formatted_odds, formatted_api_data = formatted_api_data)