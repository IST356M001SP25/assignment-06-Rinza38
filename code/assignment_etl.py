# Import required libraries
import streamlit as st  # For creating web apps and data visualization
import pandas as pd  # For data manipulation and analysis
import requests  # For making HTTP requests
import json  # For working with JSON data

# Handle imports differently depending on whether this is run directly or imported as a module
if __name__ == "__main__":
    import sys
    sys.path.append('code')  # Add 'code' directory to Python path
    from apicalls import get_google_place_details, get_azure_sentiment, get_azure_named_entity_recognition
else:
    from code.apicalls import get_google_place_details, get_azure_sentiment, get_azure_named_entity_recognition

# Define file paths for caching data
PLACE_IDS_SOURCE_FILE = "cache/place_ids.csv"  # Source file containing Google Place IDs
CACHE_REVIEWS_FILE = "cache/reviews.csv"  # Cache file for storing reviews data
CACHE_SENTIMENT_FILE = "cache/reviews_sentiment_by_sentence.csv"  # Cache file for sentiment analysis results
CACHE_ENTITIES_FILE = "cache/reviews_sentiment_by_sentence_with_entities.csv"  # Cache file for entity recognition results


def reviews_step(place_ids: str|pd.DataFrame) -> pd.DataFrame:
    '''
    Process Google Place IDs to extract and transform reviews data.
    
    Pipeline Step 1: place_ids --> reviews_step --> reviews (place_id, name, author_name, rating, text)
    
    Args:
        place_ids: Either a file path (str) to CSV containing Google Place IDs or a DataFrame
        
    Returns:
        DataFrame containing reviews with columns:
        - place_id: Google Place ID
        - name: Name of the place
        - author_name: Name of the review author
        - rating: Review rating (1-5)
        - text: Review text content
        
    The function caches results to CACHE_REVIEWS_FILE
    '''

    # Load data - handle both file path and DataFrame inputs
    if isinstance(place_ids, str):
        place_ids_df = pd.read_csv(place_ids)
    else:
        place_ids_df = place_ids

    # TRANSFORMATIONS

    # Get detailed information for each place from Google Places API
    google_places = []
    for index, row in place_ids_df.iterrows():
        place = get_google_place_details(row['Google Place ID'])
        google_places.append(place['result'])  # Store the detailed place information

    # Convert nested JSON structure to flat DataFrame
    # Extract reviews while preserving place metadata
    reviews_df = pd.json_normalize(google_places, record_path="reviews", meta=["place_id", 'name'])

    # Select only the columns we need
    reviews_df = reviews_df[['place_id', 'name', 'author_name', 'rating', 'text']]

    # Cache and return results
    reviews_df.to_csv(CACHE_REVIEWS_FILE, index=False, header=True)
    return reviews_df

def sentiment_step(reviews: str|pd.DataFrame) -> pd.DataFrame:
    '''
    Perform sentiment analysis on reviews at the sentence level.
    
    Pipeline Step 2: reviews --> sentiment_step --> review_sentiment_by_sentence
    
    Args:
        reviews: Either a file path (str) to CSV containing reviews or a DataFrame
        
    Returns:
        DataFrame containing sentence-level sentiment analysis with columns:
        - place_id, name, author_name, rating: From original review
        - sentence_text: Individual sentence from review
        - sentence_sentiment: Overall sentiment of sentence (positive/neutral/negative)
        - confidenceScores.positive/neutral/negative: Confidence scores for each sentiment
        
    The function caches results to CACHE_SENTIMENT_FILE
    '''

    # Load data - handle both file path and DataFrame inputs
    if isinstance(reviews, str):
        reviews_df = pd.read_csv(reviews)
    else:
        reviews_df = reviews

    # TRANSFORMATIONS

    # Perform sentiment analysis for each review text
    sentiments = []
    for index, row in reviews_df.iterrows():
        sentiment = get_azure_sentiment(row['text'])
        sentiment_item = sentiment['results']['documents'][0]  # Extract sentiment data
        # Preserve original review metadata
        sentiment_item['place_id'] = row['place_id']
        sentiment_item['name'] = row['name']
        sentiment_item['author_name'] = row['author_name']
        sentiment_item['rating'] = row['rating']
        sentiments.append(sentiment_item)

    # Convert nested sentiment data to flat DataFrame
    sentiment_df = pd.json_normalize(sentiments, record_path="sentences", 
                                   meta=["place_id", 'name', 'author_name', 'rating'])
    
    # Clean up column names
    sentiment_df.rename(columns={
        'text': 'sentence_text',
        'sentiment': 'sentence_sentiment'
    }, inplace=True)

    # Select and order columns for output
    sentiment_df = sentiment_df[['place_id', 'name', 'author_name', 'rating', 'sentence_text', 
                               'sentence_sentiment', 'confidenceScores.positive', 
                               'confidenceScores.neutral', 'confidenceScores.negative']]

    # Cache and return results
    sentiment_df.to_csv(CACHE_SENTIMENT_FILE, index=False, header=True)
    return sentiment_df

def entity_extraction_step(sentiment: str|pd.DataFrame) -> pd.DataFrame:
    '''
    Extract named entities from sentiment-analyzed sentences.
    
    Pipeline Step 3: review_sentiment_by_sentence --> entity_extraction_step --> review_sentiment_entities_by_sentence
    
    Args:
        sentiment: Either a file path (str) to CSV containing sentiment data or a DataFrame
        
    Returns:
        DataFrame containing extracted entities with columns:
        - All columns from sentiment analysis
        - entity_text: The extracted entity text
        - entity_category: Entity category (e.g., Person, Location)
        - entity_subcategory: More specific classification
        - confidenceScores.entity: Confidence score for entity recognition
        
    The function caches results to CACHE_ENTITIES_FILE
    '''

    # Load data - handle both file path and DataFrame inputs
    if isinstance(sentiment, str):
        sentiment_df = pd.read_csv(sentiment)
    else:
        sentiment_df = sentiment

    # TRANSFORMATIONS

    # Perform entity recognition for each sentence
    entities = []
    for index, row in sentiment_df.iterrows():
        entity = get_azure_named_entity_recognition(row['sentence_text'])
        entity_item = entity['results']['documents'][0]
        # Preserve all original sentiment analysis data
        for col in sentiment_df.columns:
            entity_item[col] = row[col]    
        entities.append(entity_item)

    # Convert nested entity data to flat DataFrame
    entities_df = pd.json_normalize(entities, record_path="entities", 
                                  meta=list(sentiment_df.columns))

    # Clean up column names
    entities_df.rename(columns={
        'text': 'entity_text',
        'category': 'entity_category',
        'subcategory': 'entity_subcategory',
        'confidenceScore': 'confidenceScores.entity'
    }, inplace=True)   

    # Select and order columns for output
    entities_df = entities_df[['place_id', 'name', 'author_name', 'rating', 'sentence_text', 
                             'sentence_sentiment', 'confidenceScores.positive', 
                             'confidenceScores.neutral', 'confidenceScores.negative', 
                             'entity_text', 'entity_category', 'entity_subcategory', 
                             'confidenceScores.entity']]

    # Cache and return results
    entities_df.to_csv(CACHE_ENTITIES_FILE, index=False, header=True)
    return entities_df

# Main execution block - runs when script is executed directly
if __name__ == '__main__':
    # Execute the full data processing pipeline
    reviews_step(PLACE_IDS_SOURCE_FILE)  # Step 1: Get reviews
    sentiment_step(CACHE_REVIEWS_FILE)  # Step 2: Analyze sentiment
    entities_df = entity_extraction_step(CACHE_SENTIMENT_FILE)  # Step 3: Extract entities
    
    # Display results using Streamlit for debugging/exploration
    st.write(entities_df)