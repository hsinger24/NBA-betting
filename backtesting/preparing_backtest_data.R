########## Setting working directory and imports ##########
setwd("~/Desktop/NBA-betting")
logistic_model = readRDS('logistic_model.rds')
library(readxl)

########## Importing data and getting test data ##########

# Reading in and attaching data
data = read.csv('data/final_dataset.csv')
data = subset(data, select = -c(1, 41, 108:209))
attach(data)
# Converting binary to factors
data$Team1_Won = factor(as.character(data$Team1_Won), levels = c('0','1'), labels = c('L', 'W'))
data$Team1_is_B2B = factor(as.character(data$Team1_is_B2B), levels = c('0','1'), labels = c('N', 'Y'))
data$Team1_is_B2B_First = factor(as.character(data$Team1_is_B2B_First), levels = c('0','1'), labels = c('N', 'Y'))
data$Team1_is_B2B_Second = factor(as.character(data$Team1_is_B2B_Second), levels = c('0','1'), labels = c('N', 'Y'))
data$Team1_is_Home = factor(as.character(data$Team1_is_Home), levels = c('0','1'), labels = c('N', 'Y'))
data$Team1_is_B2B_Opp = factor(as.character(data$Team1_is_B2B_Opp), levels = c('0','1'), labels = c('N', 'Y'))
data$Team1_is_B2B_First_Opp = factor(as.character(data$Team1_is_B2B_First_Opp), levels = c('0','1'), labels = c('N', 'Y'))
data$Team1_is_B2B_Second_Opp = factor(as.character(data$Team1_is_B2B_Second_Opp), levels = c('0','1'), labels = c('N', 'Y'))
data$Team1_is_Home_Opp = factor(as.character(data$Team1_is_Home_Opp), levels = c('0','1'), labels = c('N', 'Y'))
# Getting test data
train = (Game_ID>21700001 & Game_ID<21800001)
test_data = data[train, ]
test_data = test_data[160:1214,]
test_data[,'Team1_Win_Prob'] = predict(logistic_model, test_data, type = 'raw')
#test_target = Team1_Won[train]
#test_target = test_target[160:1214]
#predictions = predict(logistic_model, test_data, type = 'raw')
#predictions = ifelse(predictions>0.5, 1,0)
#mean(predictions==test_target)
# Getting odds data
odds = read.csv('data/odds_2017_test.csv')
odds = subset(odds, select = c(32,5,6,14,26))
colnames(odds) = c('Game_ID', 'Team1', 'Team2', 'ML1', 'ML2')
# Merging test_data and odds
test_merged = merge(test_data, odds, by = 'Game_ID')
write.csv(test_merged, 'data/test_merged_2017.csv')
