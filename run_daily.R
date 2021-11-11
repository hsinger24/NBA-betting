########## Setting working directory and imports ##########
setwd("~/Desktop/NBA-betting")
model = readRDS('Model_Build/logistic_model.rds')
library(MASS)
library(dplyr)
library(caret)
library(reshape2)
library(fastDummies)
library(deepnet)

########## Importing data ##########

# Reading in and attaching data
all_data_today = read.csv('current_season_data/todays_stats.csv')
data = all_data_today
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
# Getting necessary columns for prediction
inputs= subset(data, select = -c(1,2,3,4,106))

########## Making predictions ##########

all_data_today <- all_data_today %>%
  mutate(Team1_Prob = predict(object = model, inputs, type = 'raw'))

write.csv(all_data_today, 'current_season_data/todays_stats.csv')
