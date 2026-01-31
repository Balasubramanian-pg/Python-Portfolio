import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

Importing Data 

games=pd.read_csv('/kaggle/input/metacritic-scores-for-games-movies-tv-and-music/feb_2023/games.csv')
movies=pd.read_csv('/kaggle/input/metacritic-scores-for-games-movies-tv-and-music/feb_2023/movies.csv')

Games 
games.info()
games.isna().sum()

games = games[games["user_score"] != 'tbd']
games["user_score"] = games["user_score"].astype("float32")

Let's look at the top 20 games of all time by user_score and metascore 

games.sort_values(by="user_score", ascending=False).head(20)
games[["MD", "year"]] = games["release_date"].str.split(",", expand=True)
games.drop(labels=["id", "sort_no"], axis=1, inplace=True)

Platforms

f, ax = plt.subplots(figsize=(18, 4))
plt.xticks(rotation = 35)
games = games[games["platform"] != 0]
old_cons = games[(games["platform"] != "Stadia") & (games["platform"] != "Xbox Series X") & (games["platform"] != "PlayStation 5")]
# I am deleting new consoles from this boxplot since they are not in EOL stage -> comparing a few samples to many
sns.boxplot(x=old_cons["platform"], y=old_cons["user_score"])

Year by Year

games.groupby(["year"]).median()

games.sort_values(by="year", inplace=True)
good_games_user = games[games["user_score"] > 8.5]
f, ax = plt.subplots(figsize=(18, 4))
sns.histplot(games["year"])
sns.histplot(good_games_user.year)

good_games_critics = games[games["metascore"] > 85]
f, ax = plt.subplots(figsize=(18, 4))
sns.histplot(good_games_user.year)
sns.histplot(good_games_critics.year)

Correlation between metascore and user score    

label_enc = LabelEncoder()
for col in ["year", "platform"]:
    games[col] = label_enc.fit_transform(games[col])
print(games)

f, ax = plt.subplots(1,2, figsize=(12,4))
sns.histplot(games["user_score"], kde=True, ax=ax[0])
sns.histplot(games["metascore"], kde=True, ax=ax[1])    

corr = games.corr(method='spearman')
sns.heatmap(corr, annot=True)
