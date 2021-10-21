# Setting working directory and imports
setwd("~/Desktop/NBA-betting")

# Getting every year's data into one file

years = c(2007:2018)
all_games = data.frame()
colnames(all_games) = colnames(year_df)
for (year in years) {
  character_year = toString(year)
  file_path = paste('data/final_stats_', character_year, '.csv', sep = '')
  year_df = read.csv(file_path, header = T)
  if (year == 2007) {
    year_df = subset(year_df, select = -c(1,2, 211, 212))
  }
  else {
    year_df = subset(year_df, select = -c(1, 210, 211))
  }
  all_games = rbind(all_games, year_df)
}

write.csv(all_games, 'data/final_dataset.csv')
