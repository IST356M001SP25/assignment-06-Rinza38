import streamlit as st
import pandas as pd
import requests
import json 
if __name__ == "__main__":
    import sys
    sys.path.append('code')
    from apicalls import get_google_place_details, get_azure_sentiment, get_azure_named_entity_recognition
else:
    from code.apicalls import get_google_place_details, get_azure_sentiment, get_azure_named_entity_recognition

PLACE_IDS_SOURCE_FILE = "cache/place_ids.csv"
CACHE_REVIEWS_FILE = "cache/reviews.csv"
CACHE_SENTIMENT_FILE = "cache/reviews_sentiment_by_sentence.csv"
CACHE_ENTITIES_FILE = "cache/reviews_sentiment_by_sentence_with_entities.csv"


def reviews_step(place_ids: str|pd.DataFrame) -> pd.DataFrame:
    '''
      1. place_ids --> reviews_step --> reviews: place_id, name (of place), author_name, rating, text 
    '''
    # if string, then its a filename so load into dataframe
    if isinstance(place_ids, str):
        place_ids_df = pd.read_csv(place_ids)
    else:
        place_ids_df = place_ids

    # TRANSFORMATIONS

    # get google place details for each place_id
    google_places = []
    for index, row in place_ids_df.iterrows():
        place = get_google_place_details(row['place_id'])
        google_places.append(place['result'])

    # construct dataframe at the reviews level, include place_id, name from parent level
    reviews_df = pd.json_normalize(google_places, record_path="reviews", meta=["place_id", 'name'])

    # pair down to the columns we want
    reviews_df = reviews_df[['place_id', 'name', 'author_name', 'rating', 'text']]

    # save to cache, return dataframe
    reviews_df.to_csv(CACHE_REVIEWS_FILE, index=False, header=True)
    return reviews_df


def sentiment_step(reviews: str|pd.DataFrame) -> pd.DataFrame:
    '''
      2. reviews --> sentiment_step --> review_sentiment_by_sentence
    '''
    # if string, then its a filename so load into dataframe
    if isinstance(reviews, str):
        reviews_df = pd.read_csv(reviews)
    else:
        reviews_df = reviews

    # TRANSFORMATIONS

    # get sentiment for each review
    sentiments = []
    for index, row in reviews_df.iterrows():
        sentiment = get_azure_sentiment(row['text'])
        sentiment_item = sentiment['results']['documents'][0]
        sentiment_item['place_id'] = row['place_id']
        sentiment_item['name'] = row['name']
        sentiment_item['author_name'] = row['author_name']
        sentiment_item['rating'] = row['rating']
        sentiments.append(sentiment_item)

    # construct dataframe at the sentence level, include place_id, name from parent level
    sentiment_df = pd.json_normalize(sentiments, record_path="sentences", 
                                   meta=["place_id", 'name', 'author_name', 'rating'])
    
    # rename columns
    sentiment_df.rename(columns={
        'text': 'sentence_text',
        'sentiment': 'sentence_sentiment'
    }, inplace=True)

    # filter output columns
    sentiment_df = sentiment_df[['place_id', 'name', 'author_name', 'rating', 
                               'sentence_text', 'sentence_sentiment', 
                               'confidenceScores.positive', 'confidenceScores.neutral', 
                               'confidenceScores.negative']]

    # save to cache, return dataframe
    sentiment_df.to_csv(CACHE_SENTIMENT_FILE, index=False, header=True)
    return sentiment_df


def entity_extraction_step(sentiment: str|pd.DataFrame) -> pd.DataFrame:
    '''
      3. review_sentiment_by_sentence --> entity_extraction_step --> review_sentiment_entities_by_sentence
    '''
    # if string, then its a filename so load into dataframe
    if isinstance(sentiment, str):
        sentiment_df = pd.read_csv(sentiment)
    else:
        sentiment_df = sentiment

    # TRANSFORMATIONS

    # get entities for each sentence
    entities = []
    for index, row in sentiment_df.iterrows():
        entity = get_azure_named_entity_recognition(row['sentence_text'])
        entity_item = entity['results']['documents'][0]
        for col in sentiment_df.columns:
            entity_item[col] = row[col]    
        entities.append(entity_item)

    # construct dataframe at the entity level, include all parent columns
    entities_df = pd.json_normalize(entities, record_path="entities", 
                                  meta=list(sentiment_df.columns))

    # rename columns
    entities_df.rename(columns={
        'text': 'entity_text',
        'category': 'entity_category',
        'subCategory': 'entity_subCategory',
        'confidenceScore': 'confidenceScores.entity'
    }, inplace=True)

    # filter output columns
    entities_df = entities_df[['place_id', 'name', 'author_name', 'rating', 
                             'sentence_text', 'sentence_sentiment', 
                             'confidenceScores.positive', 'confidenceScores.neutral', 
                             'confidenceScores.negative', 'entity_text', 
                             'entity_category', 'entity_subCategory', 
                             'confidenceScores.entity']]

    # save to cache, return dataframe
    entities_df.to_csv(CACHE_ENTITIES_FILE, index=False, header=True)
    return entities_df


if __name__ == '__main__':
    import streamlit as st  # helpful for debugging as you can view your dataframes and json outputs

    reviews_step(PLACE_IDS_SOURCE_FILE)
    sentiment_step(CACHE_REVIEWS_FILE)
    entities_df = entity_extraction_step(CACHE_SENTIMENT_FILE)
    st.write(entities_df)