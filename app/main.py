from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import joblib
import pickle
from fastapi.middleware.cors import CORSMiddleware

from app.destination_recommendations import get_recommendations
from app.itinerary_generator import generate_itinerary

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

knn_model = joblib.load('app/model/knn_model.joblib')
label_encoders = pickle.load(open('app/model/label_encoders.pkl', 'rb'))
mlb = pickle.load(open('app/model/mlb.pkl', 'rb'))

# if not isinstance(knn_model, KNeighborsClassifier):
#     raise ValueError("The loaded model is not an instance of KNeighborsClassifier.")

class UserData(BaseModel):
    age_category: str
    gender: str
    nationality: str
    traveler_category: str
    city: str
    interests: List[str]  
    duration: int 


@app.post("/recommendations/")
def get_itinerary(user_data: UserData):
    try:
        # Recommendations based on user data
        recommendations = get_recommendations(knn_model, label_encoders, mlb, user_data.dict())

        recommendations_list = [rec['Name'] for rec in recommendations]

        # Pass recommendations to itinerary generator
        itinerary = generate_itinerary(recommendations_list, user_data.city, user_data.duration)
        
        return itinerary

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))