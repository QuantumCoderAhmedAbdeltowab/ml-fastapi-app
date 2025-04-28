# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import re
# import pickle
# from feature import FeatureExtraction  # For URL feature extraction

# app = FastAPI()

# # Load URL detection model
# try:
#     with open("model_url_v2.pkl", "rb") as f:
#         url_model = pickle.load(f)
# except Exception as e:
#     raise RuntimeError("Failed to load model_url_v2.pkl") from e

# # Load SMS detection model (pipeline handles SMS feature extraction internally)
# try:
#     with open("model_sms_v1.pkl", "rb") as f:
#         sms_model = pickle.load(f)
# except Exception as e:
#     raise RuntimeError("Failed to load model_sms_v1.pkl") from e

# class URLRequest(BaseModel):
#     url: str

# class SMSRequest(BaseModel):
#     message: str

# @app.post("/predict_url")
# async def predict_url(request: URLRequest):
#     try:
#         # Use the feature extraction function from feature.py
#         features = FeatureExtraction(request.url)
#         prediction = url_model.predict([features])
#         return {"prediction": int(prediction[0])}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/predict_sms")
# async def predict_sms(request: SMSRequest):
#     try:
#         sms_message = request.message

#         # Directly pass the SMS message to the SMS model's pipeline
#         sms_prediction = sms_model.predict([sms_message])

#         # Check if the SMS contains any URL using a regex
#         url_regex = r'(https?://\S+)'  # Basic regex to capture http/https URLs
#         urls = re.findall(url_regex, sms_message)

#         url_prediction = None
#         if urls:
#             # Process the first URL found using the URL detection model
#             url = urls[0]
#             features = FeatureExtraction(url)
#             pred = url_model.predict([features])
#             url_prediction = int(pred[0])

#         return {
#             "sms_prediction": int(sms_prediction[0]),
#             "url_prediction": url_prediction,
#             "urls_found": urls
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))




from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import pickle
from feature import FeatureExtraction  # For URL feature extraction
from preprocessing import preprocess_text  # For SMS preprocessing
import nltk

# this will create tokenizers/punkt_tab/<lang>/ if possible
nltk.download('punkt_tab', quiet=True)  
# still download the real punkt too
nltk.download('punkt', quiet=True)
app = FastAPI()

# Load URL detection model
try:
    with open("model_url_v2.pkl", "rb") as f:
        url_model = pickle.load(f)
except Exception as e:
    raise RuntimeError("Failed to load model_url_v2.pkl") from e

# Load SMS detection model (expects preprocessed text)
try:
    with open("model_sms_v2.pkl", "rb") as f:
        sms_model = pickle.load(f)
except Exception as e:
    raise RuntimeError("Failed to load model_sms_v2.pkl") from e

class URLRequest(BaseModel):
    url: str

class SMSRequest(BaseModel):
    message: str

@app.post("/predict_url")
async def predict_url(request: URLRequest):
    try:
        # Extract features and predict
        features = FeatureExtraction(request.url).getFeaturesList()
        raw_pred = url_model.predict([features])[0]
        prediction = int(raw_pred)

        # Map -1 → 0, 1 → 1, others → 0
        final_result = 1 if prediction == 1 else 0

        return {
            "prediction": prediction,
            "final_result": final_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_sms")
async def predict_sms(request: SMSRequest):
    try:
        sms_message = request.message
        
        # Preprocess the SMS message
        sms_message_clean = preprocess_text(sms_message)
        
        # Predict using the SMS model (0 = unsafe, 1 = safe)
        sms_pred_int = int(sms_model.predict([sms_message_clean])[0])
        
        # Look for URLs in the SMS
        url_regex = r'(https?://\S+|www\.\S+)'  
        urls = re.findall(url_regex, sms_message)
        
        # Default URL prediction to a non-1 value
        url_pred_int = None
        if urls:
            url = urls[0]
            features = FeatureExtraction(url).getFeaturesList()
            url_pred_int = int(url_model.predict([features])[0])  # -1 = unsafe, 1 = safe
        
        # Compute final_result: 1 only if both models say "safe"
        final_result = 1 if (sms_pred_int == 1 and url_pred_int == 1) else 0
        
        return {
            "sms_prediction": sms_pred_int,
            "url_prediction": url_pred_int,
            "urls_found": urls,
            "final_result": final_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ollama_client import query_ollama
from translation_utils import detect_language, translate_text
class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint for asking cybersecurity-related questions.
    The API detects if the prompt is in Arabic, translates it to English before querying the model,
    and then translates the response back to Arabic.
    """
    try:
        # Await the asynchronous language detection
        input_language = await detect_language(request.question)
        
        # Translate to English if the question is in Arabic
        if input_language == 'ar':
            translated_question = await translate_text(request.question, 'en')
        else:
            translated_question = request.question

        # Run the blocking Ollama call in a thread to avoid blocking the event loop
        english_response = await asyncio.to_thread(query_ollama, translated_question)

        # Translate back to Arabic if necessary
        if input_language == 'ar':
            final_response = await translate_text(english_response, 'ar')
        else:
            final_response = english_response

        return {"response": final_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80)


