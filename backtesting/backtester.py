import pandas as pd

# Creating functions to later apply
def convert_odds(x):
    if x<0:
        return (abs(x)/(abs(x)+100))
    else:
        return (100/(abs(x)+100))
def kelly_criterion(row):
    if row['Team1_Prob_Diff']<0:
        return 0
    else:
        p = row['Team1_Win_Prob']
        q = 1-p
        ml = row['Team1_ML']
        if ml>=0:
            b = (ml/100)
        if ml<0:
            b = (100/abs(ml))
        kc = ((p*b) - q) / b
        if (kc > 0.5) & (kc<0.6):
            return kc/10
        if (kc > 0.6) & (kc<0.7):
            return kc/12
        if kc > 0.7:
            return kc/15
        else:
            return kc/8
def kelly_criterion_2(row):
    if row['Team2_Prob_Diff']<0:
        return 0
    else:
        p = 1 - row['Team1_Win_Prob']
        q = 1-p
        ml = row['Team2_ML']
        if ml>=0:
            b = (ml/100)
        if ml<0:
            b = (100/abs(ml))
        kc = ((p*b) - q) / b
        if (kc > 0.5) & (kc<0.6):
            return kc/10
        if (kc > 0.6) & (kc<0.7):
            return kc/12
        if kc > 0.7:
            return kc/15
        else:
            return kc/8

def backtesting(year, starting_capital, ml_param, ml_param_underdog, kelly, fixed_capital, save_file = True):
    """Backtests our model for a given year

    Args:
        year: The year in which we wish to backtest
        starting_capital: The amount of capital simulated for the model at the beginning of the year
        ml_param (must be negative): The cutoff point for large favorites not to bet on
        save_file: True if you want to save file to data folder. If false, will return the dataframe
        kelly: The fraction of a kelly that we will base our bets off
        fixed_capital: Do we update our capital on a per bet basis?

    Returns:
        DataFrame object with all games bet on and keeps track of capital
    """
    # Creating functions later applied
    def kelly_criterion(row):
        if row['Team1_Prob_Diff']<0:
            return 0
        else:
            p = row['Team1_Win_Prob']
            q = 1-p
            ml = row['Team1_ML']
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
        if row['Team2_Prob_Diff']<0:
            return 0
        else:
            p = 1 - row['Team1_Win_Prob']
            q = 1-p
            ml = row['Team2_ML']
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
    # Creating necessary columns
    test_merged = pd.read_csv('data/test_merged_' + str(year) + '.csv', index_col = 0)
    test_merged['Team1_ML'] = 0
    test_merged['Team2_ML'] = 0
    for index, row in test_merged.iterrows():
        if row['Team1.x']==row['Team1.y']:
            test_merged.loc[index, 'Team1_ML'] = row['ML1']
            test_merged.loc[index, 'Team2_ML'] = row['ML2']
        else:
            test_merged.loc[index, 'Team1_ML'] = row['ML2']
            test_merged.loc[index, 'Team2_ML'] = row['ML1']
    drop_cols = ['Team1.y', 'Team2.y', 'ML1', 'ML2']
    test_merged.drop(drop_cols, axis = 1, inplace = True)
    test_merged['Team1_ML_Prob'] = test_merged['Team1_ML'].apply(convert_odds)
    test_merged['Team2_ML_Prob'] = test_merged['Team2_ML'].apply(convert_odds)
    test_merged['Team1_Prob_Diff'] = test_merged['Team1_Win_Prob'] - test_merged['Team1_ML_Prob']
    test_merged['Team2_Prob_Diff'] = (1-test_merged['Team1_Win_Prob']) - test_merged['Team2_ML_Prob']
    test_merged['Team1_KC'] = test_merged.apply(kelly_criterion, axis = 1)
    test_merged['Team2_KC'] = test_merged.apply(kelly_criterion_2, axis = 1)

    # Only getting columns I need
    keep_columns = ['Game_ID', 'Date', 'Team1.x', 'Team2.x']+list(test_merged.columns)[-10:]
    test_merged = test_merged[keep_columns]
    test_merged.columns = ['Game_ID', 'Date', 'Team1', 'Team2', 'Team1_Won', 'Team1_Win_Prob', 'Team1_ML', 
    'Team2_ML', 'Team1_ML_Prob', 'Team2_ML_Prob', 'Team1_Prob_Diff', 'Team2_Prob_Diff', 'Team1_KC', 'Team2_KC']
    test_merged.reset_index(drop = True, inplace = True)

    # Tracking results
    test_merged['Team1_Bet'] = 0
    test_merged['Team2_Bet'] = 0
    test_merged['Money_Tracker'] = 0
    test_merged['Bet_Won'] = 0
    for index, row in test_merged.iterrows():
        payoff1 = 0
        payoff2 = 0
        if index == 0:

             # Passing over rows where there is no/small perceived advatage
            if (row.Team1_KC == 0) & (row.Team2_KC == 0):
                test_merged.loc[index, 'Money_Tracker'] = starting_capital
                continue
            if ((row.Team1_Prob_Diff<0) & (row.Team2_Prob_Diff<.01)) | ((row.Team1_Prob_Diff<0.01) & (row.Team2_Prob_Diff<0)):
                test_merged.loc[index, 'Money_Tracker'] = starting_capital
                continue

            # Setting bet amount
            if row.Team1_KC>0:
                test_merged.loc[index, 'Team1_Bet'] = starting_capital*row.Team1_KC
            if row.Team2_KC>0:
                test_merged.loc[index, 'Team2_Bet'] = starting_capital*row.Team2_KC
        
            # Setting payoffs
            if test_merged.loc[index, 'Team1_Bet']>0:
                if row.Team1_ML<0:
                    payoff1 = (test_merged.loc[index, 'Team1_Bet']/abs(row.Team1_ML))*100
                if row.Team1_ML>0:
                    payoff1 = test_merged.loc[index, 'Team1_Bet'] * (row.Team1_ML/100)
            if test_merged.loc[index, 'Team2_Bet']>0:
                if row.Team2_ML<0:
                    payoff2 = (test_merged.loc[index, 'Team2_Bet']/abs(row.Team2_ML))*100
                if row.Team2_ML>0:
                    payoff2 = test_merged.loc[index, 'Team2_Bet'] *(row.Team2_ML/100)

            # Passing over huge favorites/underdogs
            if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_ML<ml_param):
                test_merged.loc[index, 'Money_Tracker'] = starting_capital
                continue
            if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_ML<ml_param):
                test_merged.loc[index, 'Money_Tracker'] = starting_capital
                continue
            if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_ML>ml_param_underdog):
                test_merged.loc[index, 'Money_Tracker'] = starting_capital
                continue
            if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_ML>ml_param_underdog):
                test_merged.loc[index, 'Money_Tracker'] = starting_capital
                continue
        
            # Updating total amount of money based on results
            if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_Won == 'W'):
                test_merged.loc[index, 'Money_Tracker'] = starting_capital + payoff1
            if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_Won == 'L'):
                test_merged.loc[index, 'Money_Tracker'] = starting_capital + payoff2
            if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_Won == 'L'):
                test_merged.loc[index, 'Money_Tracker'] = starting_capital - test_merged.loc[index, 'Team1_Bet']
            if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_Won == 'W'):
                test_merged.loc[index, 'Money_Tracker'] = starting_capital - test_merged.loc[index, 'Team2_Bet']
    
        else:

             # Passing over rows where there is no/small perceived advatage
            if (row.Team1_KC == 0) & (row.Team2_KC == 0):
                test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker']
                continue
            if ((row.Team1_Prob_Diff<0) & (row.Team2_Prob_Diff<.01)) | ((row.Team1_Prob_Diff<0.01) & (row.Team2_Prob_Diff<0)):
                test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker']
                continue
            
            # Setting bet amount
            if fixed_capital:
                if row.Team1_KC>0:
                    test_merged.loc[index, 'Team1_Bet'] = starting_capital*row.Team1_KC
                if row.Team2_KC>0:
                    test_merged.loc[index, 'Team2_Bet'] = starting_capital*row.Team2_KC
            else:
                if row.Team1_KC>0:
                    test_merged.loc[index, 'Team1_Bet'] = test_merged.loc[(index-1), 'Money_Tracker']*row.Team1_KC
                if row.Team2_KC>0:
                    test_merged.loc[index, 'Team2_Bet'] = test_merged.loc[(index-1), 'Money_Tracker']*row.Team2_KC

            # Setting payoffs
            if test_merged.loc[index, 'Team1_Bet']>0:
                if row.Team1_ML<0:
                    payoff1 = (test_merged.loc[index, 'Team1_Bet']/abs(row.Team1_ML))*100
                if row.Team1_ML>0:
                    payoff1 = test_merged.loc[index, 'Team1_Bet'] * (row.Team1_ML/100)
            if test_merged.loc[index, 'Team2_Bet']>0:
                if row.Team2_ML<0:
                    payoff2 = (test_merged.loc[index, 'Team2_Bet']/abs(row.Team2_ML))*100
                if row.Team2_ML>0:
                    payoff2 = test_merged.loc[index, 'Team2_Bet'] *(row.Team2_ML/100)
            
            # Passing over huge favorites/underdogs
            if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_ML<ml_param):
                test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker']
                continue
            if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_ML<ml_param):
                test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker']
                continue
            if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_ML>ml_param_underdog):
                test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker']
                continue
            if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_ML>ml_param_underdog):
                test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker']
                continue
            
            # Updating total amount of money based on results
            if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_Won == 'W'):
                test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker'] + payoff1
            if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_Won == 'L'):
                test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker'] + payoff2
            if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_Won == 'L'):
                test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker'] - test_merged.loc[index, 'Team1_Bet']
            if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_Won == 'W'):
                test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker'] - test_merged.loc[index, 'Team2_Bet']
    
    # Tracking binary bet result
    for index, row in test_merged.iterrows():
        if index>0:
            last_game_capital = test_merged.loc[(index-1), 'Money_Tracker']
            if row.Money_Tracker>last_game_capital:
                test_merged.loc[index, 'Bet_Won'] = 1
            else:
                pass
            if row.Money_Tracker==last_game_capital:
                test_merged.loc[index, 'Bet_Won'] = -1
        if index==0:
            if row.Money_Tracker>starting_capital:
                test_merged.loc[index, 'Bet_Won'] = 1
            else:
                pass
            if row.Money_Tracker==starting_capital:
                test_merged.loc[index, 'Bet_Won'] = -1

    # Saving file if save_file argument is true
    if save_file:
        test_merged.to_csv('data/test_kc_'+str(year)+'.csv')
        return test_merged
    else:
        return test_merged

def backtesting_win_pct(backtester):
    """Finds win pct from a df where bet tracking is completed

    Args:
        backtester: result of backtesting function from a given year

    Returns:
        Win percentage of bets from that year
    """
    backtester = backtester[backtester.Bet_Won>-1]
    return backtester['Bet_Won'].mean()

def backtesting_bins(backtester, prob_calibration =  False, kc_bins = False):
    """Determines how well calibrated the model's probabilities are

    Args:
        backtester: result of backtesting function from a given year
        prob_calibration: If true, will return the probability that team 1 wins by 10% win_prob bins
        kc_bins: If true, will return overall winnings/losses by KC bins
    Returns:
        Depending on which argument we put to be true
    """

    # Tests how often team 1 wins binned by prediction probability
    if prob_calibration:
        # Binnning by 10% Team_1_Win_Prob
        bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        labels = ['<10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '>90%']
        backtester['Bin'] = pd.cut(backtester['Team1_Win_Prob'], bins = bins, labels = labels)

        # Grouping by bin
        grouped = backtester.groupby('Bin')['Team1_Win_Prob'].mean()
        return grouped

    if kc_bins:
        backtester = backtester[backtester.Bet_Won>-1]

        #Getting winnings/loss for each game
        backtester['Games_Winnings'] = 0
        backtester.reset_index(drop = True, inplace = True)
        for index, row in backtester.iterrows():
            if index == 0:
                continue
            else:
                backtester.loc[index, 'Games_Winnings'] = backtester.loc[index, 'Money_Tracker'] - backtester.loc[(index-1), 'Money_Tracker']

        #Binning by KC, returning winnings/losses by group
        backtester['Overall_KC'] = backtester.Team1_KC + backtester.Team2_KC
        bins = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 1]
        labels = ['<1%', '1-2%', '2-3%', '3-4%', '4-5%', '5-6%', '6-7%', '7-8%', '8-9%', '9-10%', '>10%']
        backtester['KC_Bins'] = pd.cut(backtester['Overall_KC'], bins = bins, labels = labels)
        grouped = backtester.groupby(backtester['KC_Bins'])['Games_Winnings'].sum()
        return grouped

# backtester = backtesting(2018, 100000, -1750, 1000, kelly = 12, fixed_capital = False, save_file=False)
# print(backtester.tail())



#Results by changing parameters
returns = pd.DataFrame(columns = ['Year', 'ml_500', 'ml_750', 'ml_1000', 'ml_1250', 'ml_1500', 'ml_1750', 'ml_2000'])
for year in list(range(2012,2019)):
    result = []
    for ml_param in [500, 750, 1000, 1250, 1500, 1750, 2000]:
        backtester = backtesting(year, 100000, -1750, ml_param, kelly = 12, fixed_capital = False, save_file=False)
        final_capital = backtester.loc[len(backtester)-1, 'Money_Tracker']
        returns_value = final_capital/100000
        result.append(returns_value)
    series = [year] + result
    series = pd.Series(series, index = returns.columns)
    returns = returns.append(series, ignore_index = True)
returns.to_csv('data/changing_ml_underdog_results.csv')

##### Best kelly = 11 or 12 - Best return is 12.74% (with OG Kelly 2/4/7)
##### Best ML param for favorites = -1750 - Best return is 13.01% (with OG kelly 2/4/7)
##### Bes return for ML underdog param is 1000. Ups return w/ above parameters to 17%
    