import pandas as pd

users = pd.read_csv('app/data/users.csv')
interactions = pd.read_csv('app/data/interactions.csv')
destinations = pd.read_csv('app/data/destinations.csv')

def get_recommendations(model, label_encoders, mlb, user_data):
    def calculate_interest_score(destination_tags, input_interests):
        # destination_tags_set = set(destination_tags.split(', '))
        # input_interests_set = set(input_interests.split(', '))
    
    #    Ensure both destination_tags and input_interests are strings
        destination_tags_str = ', '.join(destination_tags) if isinstance(destination_tags, list) else destination_tags
        input_interests_str = ', '.join(input_interests) if isinstance(input_interests, list) else input_interests
    
        destination_tags_set = set(destination_tags_str.split(', '))
        input_interests_set = set(input_interests_str.split(', '))
        # Intersection of input interests and destination tags
        match_count = len(destination_tags_set.intersection(input_interests_set))
        return match_count
    
    def get_similar_users_and_destinations(model, age_category, gender, nationality, traveler_category, interests):
    # Encode the inputs
        encoded_input = {
            'Age_Category': label_encoders['Age_Category'].transform([age_category])[0],
            'Gender': label_encoders['Gender'].transform([gender])[0],
            'Nationality': label_encoders['Nationality'].transform([nationality])[0],
            'Traveler_Category': label_encoders['Traveler_Category'].transform([traveler_category])[0],
        }
        # interests_vector = mlb.transform([interests.split(', ')])[0]
          # Convert interests list to a comma-separated string
        interests_str = ', '.join(interests) if isinstance(interests, list) else interests
        interests_vector = mlb.transform([interests_str])[0]

        # Combine the encoded inputs into a single array
        input_vector = [
            encoded_input['Age_Category'], 
            encoded_input['Gender'],
            encoded_input['Nationality'], 
            encoded_input['Traveler_Category']
        ]

        # Apply a higher weight to the interests vector
        weighted_interests_vector = interests_vector * 3  # Adjust weight based on importance
        input_vector.extend(weighted_interests_vector)

        # Find the top 5 similar users using the passed model
        distances, indices = model.kneighbors([input_vector])
        similar_users = users.iloc[indices[0]]
        similar_user_ids = similar_users['User_ID'].values

        # Retrieve the destinations visited by these similar users
        similar_destinations = interactions[interactions['UserID'].isin(similar_user_ids)]['DestinationID'].unique()
        result_destinations = destinations[destinations['Destination_ID'].isin(similar_destinations)]

        # Calculate an interest score for each destination based on input interests
        result_destinations['Interest_Score'] = result_destinations['Tags'].apply(lambda x: calculate_interest_score(x, interests))
    
        # Sort the destinations by the interest score
        result_destinations = result_destinations.sort_values(by='Interest_Score', ascending=False)

        return similar_users, result_destinations
    
    def independent_content_based_filtering(interests, destinations):
        # Calculate interest score 
        # destinations['Interest_Score'] = destinations['Tags'].apply(lambda x: calculate_interest_score(x, interests))
        interests_str = ', '.join(interests) if isinstance(interests, list) else interests
    
        # Calculate interest score 
        destinations['Interest_Score'] = destinations['Tags'].apply(lambda x: calculate_interest_score(x, interests_str))
        # Sort in descending order
        sorted_destinations = destinations.sort_values(by='Interest_Score', ascending=False)
    
        # print("Independent Content-Based Filtering Results:")
        # print(sorted_destinations[['Name', 'Interest_Score']])
    
        return sorted_destinations
    
    def combine_and_weight_recommendations(collab_destinations, independent_destinations, weight_collab=0.3, weight_independent=0.7):
    
        collab_destinations = collab_destinations[['Destination_ID', 'Interest_Score']]
        independent_destinations = independent_destinations[['Destination_ID', 'Interest_Score']]
    
        # Combine
        combined_destinations = pd.merge(collab_destinations, independent_destinations, on='Destination_ID', how='outer', suffixes=('_collab', '_independent'))
    
        # Fill NaN with 0
        combined_destinations['Interest_Score_collab'].fillna(0, inplace=True)
        combined_destinations['Interest_Score_independent'].fillna(0, inplace=True)
    
        # Weighted score calculation
        combined_destinations['Weighted_Score'] = (combined_destinations['Interest_Score_collab'] * weight_collab +
                                               combined_destinations['Interest_Score_independent'] * weight_independent)
    
        # Sort descending weighted score
        top_recommendations = combined_destinations.sort_values(by='Weighted_Score', ascending=False)
    
        # Fetch names
        top_recommendations = top_recommendations.merge(destinations[['Destination_ID', 'Name']], on='Destination_ID')
    
        top_recommendations = top_recommendations.head(30)
    
        # print("Combined and Weighted Recommendations:")
        # print(top_recommendations[['Name', 'Weighted_Score']])
    
        # return top_recommendations
        return top_recommendations.to_dict(orient='records')

    

    # Step 1: Extract data from user input
    age_category = user_data['age_category']
    gender = user_data['gender']
    nationality = user_data['nationality']
    traveler_category = user_data['traveler_category']
    interests = user_data['interests']

    # Step 2: Collaborative Filtering - Get similar users and destinations
    similar_users, collab_destinations = get_similar_users_and_destinations(model, age_category, gender, nationality, traveler_category, interests)

    # Step 3: Independent Content-Based Filtering
    independent_destinations = independent_content_based_filtering(interests, destinations)

    # Step 4: Combine and Weight Recommendations
    final_recommendations = combine_and_weight_recommendations(collab_destinations, independent_destinations)

    return final_recommendations


