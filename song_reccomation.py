
import pandas as pd
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt



songs_df = pd.read_csv('songs.csv')
ratings_df = pd.read_csv('ratings.csv')

songs_df.head()

#  Use regex to find years stored within parentheses
songs_df['year'] = songs_df.title.str.extract('(\(\d\d\d\d\))',expand=False)
songs_df['year'] = songs_df.year.str.extract('(\d\d\d\d)',expand=False)
songs_df['title'] = songs_df.title.str.replace('(\(\d\d\d\d\))', '')
songs_df['title'] = songs_df['title'].apply(lambda x: x.strip())

songs_df.head()


songs_df = songs_df.drop('genres', 1)

songs_df.head()
ratings_df.head()

ratings_df = ratings_df.drop('timestamp', 1)

ratings_df.head()

userInput = [
            {'title':'Beyonce', 'rating': 5},
            {'title':'Weezer', 'rating': 1},
            {'title':'Big Sean', 'rating': 3},
            {'title':"Shawn Mendes", 'rating': 5},
            {'title':'Arianna Grande', 'rating': 4}
         ]
input_songs = pd.DataFrame(userInput)
input_songs


inputId = songs_df[songs_df['title'].isin(input_songs['title'].tolist())]

input_songs = pd.merge(inputId, input_songs)
input_songs = input_songs.drop('year', 1)

input_songs

userSubset = ratings_df[ratings_df['song_id'].isin(input_songs['song_id'].tolist())]
userSubset.head()

userSubsetGroup = userSubset.groupby(['user_id'])

userSubsetGroup.get_group(1130)


userSubsetGroup = sorted(userSubsetGroup,  key=lambda x: len(x[1]), reverse=True)

userSubsetGroup[0:3]
userSubsetGroup = userSubsetGroup[0:100]

pearson_corr_dict = {}


for name, group in userSubsetGroup:

    group = group.sort_values(by='song_id')
    input_songs = input_songs.sort_values(by='song_id')

    n_ratings = len(group)

    temp_df = input_songs[input_songs['song_id'].isin(group['song_id'].tolist())]
    temp_rating_list = temp_df['rating'].tolist()
    temp_group_list = group['rating'].tolist()
    Sxx = sum([i ** 2 for i in temp_rating_list]) - pow(sum(temp_rating_list), 2) / float(n_ratings)
    Syy = sum([i ** 2 for i in temp_group_list]) - pow(sum(temp_group_list), 2) / float(n_ratings)
    Sxy = sum(i * j for i, j in zip(temp_rating_list, temp_group_list)) - sum(temp_rating_list) * sum(temp_group_list) / float(
        n_ratings)

    if Sxx != 0 and Syy != 0:
        pearson_corr_dict[name] = Sxy / sqrt(Sxx * Syy)
    else:
        pearson_corr_dict[name] = 0


pearson_corr_dict.items()

pearson_df = pd.DataFrame.from_dict(pearson_corr_dict, orient='index')
pearson_df.columns = ['similarityIndex']
pearson_df['user_id'] = pearson_df.index
pearson_df.index = range(len(pearson_df))
pearson_df.head()

top_user = pearson_df.sort_values(by='similarityIndex', ascending=False)[0:50]
top_user.head()

top_user_rating=top_user.merge(ratings_df, left_on='user_id', right_on='user_id', how='inner')
top_user_rating.head()

#  Multiplies the user's rating and similarity
top_user_rating['weightedRating'] = top_user_rating['similarityIndex']*top_user_rating['rating']
top_user_rating.head()

#  Creates a sum to the top user after sorting
temp_top_user_rating = top_user_rating.groupby('song_id').sum()[['similarityIndex','weightedRating']]
temp_top_user_rating.columns = ['sum_similarityIndex','sum_weightedRating']
temp_top_user_rating.head()

#  Create empty dataframe and get weighted avg
recommendation_df = pd.DataFrame()
recommendation_df['weighted average recommendation score'] = temp_top_user_rating['sum_weightedRating']/temp_top_user_rating['sum_similarityIndex']
recommendation_df['song_id'] = temp_top_user_rating.index
recommendation_df.head()

recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending=False)
recommendation_df.head(10)

songs_df.loc[songs_df['song_id'].isin(recommendation_df.head(10)['song_id'].tolist())]

