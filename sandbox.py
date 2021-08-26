import pandas as pd

def convert_odds(x):
    if x<0:
        return (abs(x)/(abs(x)+100))
    else:
        return (100/(abs(x)+100))

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
print(test_merged.head())