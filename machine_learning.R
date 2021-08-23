########## Setting working directory and imports ##########
setwd("~/Desktop/NBA-betting")
library(MASS)
library(dplyr)
library(caret)
library(reshape2)


########## Importing data and splitting test and train ##########

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
# Getting training data
train = (Game_ID<21800001)
training_data = data[train, ]
training_data = subset(training_data, select = -c(1,2,3,4,106))
training_target = Team1_Won[train]
# Getting test data
test_data = data[!train, ]
test_data = subset(test_data, select = -c(1,2,3,4,106))
test_target = Team1_Won[!train]

########## ML ##########

# Setting hyperparameters
set.seed(5)
ctrl = trainControl(method = 'repeatedcv', number = 10, savePrediction = 'final', classProbs = T)
# Logistic Regression
logistic = train(training_data,
      training_target,
      trControl = ctrl,
      method='glm',
      family=binomial())
predictions_logistic = predict(object = logistic, test_data, type = 'raw')
prediction_accuracy_logistic = mean(predictions == test_target)
# Random Forest
forest = train(training_data,
               training_target,
               trControl = ctrl,
               method='rf')
predictions_forest = predict(object = forest, test_data, type = 'raw')
prediction_accuracy_forest = mean(predictions_forest == test_target)
# XGBOOST
xg = train(training_data,
               training_target,
               trControl = ctrl,
               method='xgbTree')
predictions_xg = predict(object = xg, test_data, type = 'raw')
prediction_accuracy_xg = mean(predictions_xg == test_target)
               
