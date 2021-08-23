########## Setting working directory and imports ##########
setwd("~/Desktop/NBA-betting")
library(MASS)
library(dplyr)
library(caret)
library(reshape2)
library(xgboost)
library(adabag)

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

# List of potential methods: https://rdrr.io/cran/caret/man/models.html

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
prediction_accuracy_logistic = mean(predictions == test_target) # 65.5%
# Random Forest
forest = train(training_data,
               training_target,
               trControl = ctrl,
               method='rf')
predictions_forest = predict(object = forest, test_data, type = 'raw')
prediction_accuracy_forest = mean(predictions_forest == test_target) # 61.5%
# XGBOOST
xg = train(training_data,
               training_target,
               trControl = ctrl,
               method='xgbTree')
predictions_xg = predict(object = xg, test_data, type = 'raw')
prediction_accuracy_xg = mean(predictions_xg == test_target) # Did not work
# Bagged AdaBoost
adaBag = train(training_data,
               training_target,
               trControl = ctrl,
               method='AdaBag')
predictions_adaBag = predict(object = adaBag, test_data, type = 'raw')
prediction_accuracy_adaBag = mean(predictions_adaBag == test_target) # 64.3%
# Bayesian Additive Regression Trees
bartMachine = train(training_data,
               training_target,
               trControl = ctrl,
               method='bartMachine')
predictions_bartMachine = predict(object = bartMachine, test_data, type = 'raw')
prediction_accuracy_bartMachine= mean(predictions_bartMachine == test_target) # Did not work
# Diagonal Discriminant Analysis
dda = train(training_data,
            training_target,
            trControl = ctrl,
            method='dda')
predictions_dda = predict(object = dda, test_data, type = 'raw')
prediction_accuracy_dda= mean(predictions_dda == test_target) # Did not work
# C4.5-like Trees
c_trees = train(training_data,
                training_target,
                trControl = ctrl,
                method='J48')
predictions_c_trees = predict(object = c_trees, test_data, type = 'raw')
prediction_accuracy_c_trees= mean(predictions_c_trees == test_target) # 64%
