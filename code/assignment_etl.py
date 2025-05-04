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
    # 1. if strong, then it's filename loads into dataframe
    if isinstance(place_ids, str):
        place_ids_df = pd.read_csv(place_ids)
    else: 
        place_ids_df = place_ids

    # Google Places API returns nested 'result' with 'reviews' array
    all_reviews = []
    for _, row in place_ids_df.iterrows():
        response = get_google_place_details(row['place_id'])
        
        # Coding for missing API data
        if 'result' not in response: continue
        
        # Merging parent data (place_id/name) with child records (reviews)
        place_name = response['result'].get('name','')
        for review in response['result'].get('reviews',[]):
            review['place_id'] = row['place_id']  # Add parent ID
            review['name'] = place_name           # Add place name
            all_reviews.append(review)

    # json_normalize for nested JSON -> DataFrame conversion
    df = json_normalize(all_reviews) if all_reviews else pd.DataFrame()
    
    # Column validation/standardization
    required_cols = ['place_id','name','author_name','rating','text']
    for col in required_cols:                      # Ensure expected columns exist
        if col not in df.columns: df[col] = None
    
    df[required_cols].to_csv(CACHE_REVIEWS_FILE, index=False)
    return df



def sentiment_step(reviews: str|pd.DataFrame) -> pd.DataFrame:
    '''
      2. reviews --> sentiment_step --> review_sentiment_by_sentence
    '''
    reviews_df = pd.read_csv(reviews) if isinstance(reviews, str) else reviews

    all_sentences = []
    for _, review in reviews_df.iterrows():
        # Batch API processing pattern
        response = get_azure_sentiment(review['text'])
        
        # Azure response structure handling
        # Documents[0].sentences contains per-sentence analysis
        if not response.get('documents'): continue
        
        for sentence in response['documents'][0]['sentences']:
            # Preserving context from parent record
            sentence_data = {
                'place_id': review['place_id'],
                'name': review['name'],
                # ... other parent fields ...
                'sentence_text': sentence['text'],
                # Flattening nested confidence scores
                'confidenceScores.positive': sentence['confidenceScores']['positive']
            }
            all_sentences.append(sentence_data)

    # Building new DataFrame with normalized structure
    df = pd.DataFrame(all_sentences)
    df.to_csv(CACHE_SENTIMENT_FILE, index=False)
    return df


def entity_extraction_step(sentiment: str|pd.DataFrame) -> pd.DataFrame:
    '''
      3. review_sentiment_by_sentence --> entity_extraction_step --> review_sentiment_entities_by_sentence
    '''
    # Input now contains sentiment data from previous step
    sentiment_df = pd.read_csv(sentiment) if isinstance(sentiment, str) else sentiment

    all_entities = []
    for _, sentence_row in sentiment_df.iterrows():
        # Entity extraction at sentence granularity
        response = get_azure_named_entity_recognition(sentence_row['sentence_text'])
        
        # Handling entity-relationship data
        for entity in response.get('documents', [{}])[0].get('entities', []):
            entity_data = {
                # Carrying forward ALL parent data
                **sentence_row.to_dict(),  # All sentiment/place data
                # Entity-specific fields
                'entity_text': entity['text'],
                'entity_category': entity['category'],
                # Handling optional subcategory field
                'entity_subCategory': entity.get('subCategory', None)
            }
            all_entities.append(entity_data)

    # Final structured output for analysis
    df = pd.DataFrame(all_entities)
    df.to_csv(CACHE_ENTITIES_FILE, index=False)
    return df


if __name__ == '__main__':
    # helpful for debugging as you can view your dataframes and json outputs
    import streamlit as st 
    st.write("What do you want to debug?")