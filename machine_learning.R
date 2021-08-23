########## Setting working directory and imports ##########
setwd("~/Desktop/NBA-betting")
library(MASS)
library(dplyr)
library(caret)
library(reshape2)
library(fastDummies)
library(deepnet)

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
# Tree Augmented Naive Bayes Classifier with Attribute Weighting
awtan = train(training_data,
              training_target,
              trControl = ctrl,
              method='awtan')
predictions_awtan = predict(object = awtan, test_data, type = 'raw')
prediction_accuracy_awtan= mean(predictions_awtan == test_target) # Did not work
# Stochastic Gradient Boosting
gbm = train(training_data,
            training_target,
            trControl = ctrl,
            method='gbm')
predictions_gbm = predict(object = gbm, test_data, type = 'raw')
prediction_accuracy_gbm= mean(predictions_gbm == test_target) # 66.3
##### Stacked AutoEncoder Deep Neural Network #####
# Formatting data for DNN (Training)
training_data_dnn = data.frame(training_data)
training_data_dnn$Team1_Days_Rest_Team = as.double(training_data_dnn$Team1_Days_Rest_Team)
training_data_dnn$Team1_Days_Rest_Team_Opp = as.double(training_data_dnn$Team1_Days_Rest_Team_Opp)
training_data_dnn$Team1_Days_Next.Game = as.double(training_data_dnn$Team1_Days_Next.Game)
training_data_dnn$Team1_Days_Next.Game_Opp = as.double(training_data_dnn$Team1_Days_Next.Game_Opp)
training_data_dnn$Team1_Wins = as.double(training_data_dnn$Team1_Wins)
training_data_dnn$Team1_Wins_Opp = as.double(training_data_dnn$Team1_Wins_Opp)
training_data_dnn$Team1_Losses = as.double(training_data_dnn$Team1_Losses)
training_data_dnn$Team1_Losses_Opp = as.double(training_data_dnn$Team1_Losses_Opp)
training_data_dnn$Team1_USG_PCT_Agg = as.double(training_data_dnn$Team1_USG_PCT_Agg)
training_data_dnn$Team1_USG_PCT_Agg_Opp = as.double(training_data_dnn$Team1_USG_PCT_Agg_Opp)
training_data_dnn = subset(training_data_dnn, select = -c(86,102))
training_data_dnn = dummy_cols(training_data_dnn,  remove_most_frequent_dummy = T,
                  remove_selected_columns = T)
numerical = c()
for (i in 1:ncol(training_data_dnn)) {
  if (typeof(training_data_dnn[,i])=='double') {
    numerical = append(numerical, colnames(training_data_dnn)[i])
  }
}
norm.values = preProcess(training_data_dnn[, numerical], method = 'range')
training_data_dnn[,numerical] = predict(norm.values, training_data_dnn[, numerical])
# Formatting data for DNN (Test)
test_data_dnn = data.frame(test_data)
test_data_dnn$Team1_Days_Rest_Team = as.double(test_data_dnn$Team1_Days_Rest_Team)
test_data_dnn$Team1_Days_Rest_Team_Opp = as.double(test_data_dnn$Team1_Days_Rest_Team_Opp)
test_data_dnn$Team1_Days_Next.Game = as.double(test_data_dnn$Team1_Days_Next.Game)
test_data_dnn$Team1_Days_Next.Game_Opp = as.double(test_data_dnn$Team1_Days_Next.Game_Opp)
test_data_dnn$Team1_Wins = as.double(test_data_dnn$Team1_Wins)
test_data_dnn$Team1_Wins_Opp = as.double(test_data_dnn$Team1_Wins_Opp)
test_data_dnn$Team1_Losses = as.double(test_data_dnn$Team1_Losses)
test_data_dnn$Team1_Losses_Opp = as.double(test_data_dnn$Team1_Losses_Opp)
test_data_dnn$Team1_USG_PCT_Agg = as.double(test_data_dnn$Team1_USG_PCT_Agg)
test_data_dnn$Team1_USG_PCT_Agg_Opp = as.double(test_data_dnn$Team1_USG_PCT_Agg_Opp)
test_data_dnn = subset(test_data_dnn, select = -c(86,102))
test_data_dnn = dummy_cols(test_data_dnn,  remove_most_frequent_dummy = T,
                               remove_selected_columns = T)
numerical_test = c()
for (i in 1:ncol(test_data_dnn)) {
  if (typeof(test_data_dnn[,i])=='double') {
    numerical_test = append(numerical_test, colnames(test_data_dnn)[i])
  }
}
norm.values = preProcess(test_data_dnn[, numerical_test], method = 'range')
test_data_dnn[,numerical_test] = predict(norm.values, test_data[, numerical_test])
# DNN
dnn = train(training_data_dnn,
               training_target,
               trControl = ctrl,
               method='dnn')
test_data_final = cbind(test_data_dnn, test_target)
test_data_matrix = model.matrix(test_target~., data = test_data_final)[,-1]
predictions_dnn = nn.predict(dnn, test_data_matrix) # Not working (yet)

# Rotation Forest
# Robust SIMCA
# Oblique Random Forest
# Multilayer Perceptron Network with Weight Decay
