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
        return kc/8

# Creating necessary columns
test_merged = pd.read_csv('data/test_merged.csv', index_col = 0)
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
for index, row in test_merged.iterrows():
    # Passing over rows where there is no perceived advatage
    if (row.Team1_KC == 0) & (row.Team2_KC == 0):
        test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker']
        continue

    payoff1 = 0
    payoff2 = 0
    if index == 0:

        # Setting bet amount
        if row.Team1_KC>0:
            test_merged.loc[index, 'Team1_Bet'] = 100000*row.Team1_KC
        if row.Team2_KC>0:
            test_merged.loc[index, 'Team2_Bet'] = 100000*row.Team2_KC
    
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

        # Passing over huge favorites
        if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_ML<-1000):
            test_merged.loc[index, 'Money_Tracker'] = 100000
            continue
        if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_ML<-1000):
            test_merged.loc[index, 'Money_Tracker'] = 100000
            continue
    
        # Updating total amount of money based on results
        if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_Won == 'W'):
            test_merged.loc[index, 'Money_Tracker'] = 100000 + payoff1
        if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_Won == 'L'):
            test_merged.loc[index, 'Money_Tracker'] = 100000 + payoff2
        if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_Won == 'L'):
            test_merged.loc[index, 'Money_Tracker'] = 100000 - test_merged.loc[index, 'Team1_Bet']
        if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_Won == 'W'):
            test_merged.loc[index, 'Money_Tracker'] = 100000 - test_merged.loc[index, 'Team2_Bet']
    else:

        # Setting bet amount
        if row.Team1_KC>0:
            test_merged.loc[index, 'Team1_Bet'] = 100000*row.Team1_KC
        if row.Team2_KC>0:
            test_merged.loc[index, 'Team2_Bet'] = 100000*row.Team2_KC

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
        
         # Passing over huge favorites
        if (test_merged.loc[index, 'Team1_Bet']>0) & (row.Team1_ML<-1000):
            test_merged.loc[index, 'Money_Tracker'] = test_merged.loc[(index-1), 'Money_Tracker']
            continue
        if (test_merged.loc[index, 'Team2_Bet']>0) & (row.Team1_ML<-1000):
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
test_merged.to_csv('data/test_kc.csv')
