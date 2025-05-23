from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import pickle
import joblib
import nltk
from feature import FeatureExtraction
from preprocessing import preprocess_text
# from models import ChatRequest, Message, Role
# from ollama_client import chat_with_ollama
# from translation_utils import detect_language, translate_text
import shutil

# Ensure Ollama CLI is installed
# if not shutil.which("ollama"):
#     raise RuntimeError("Ollama CLI is not installed or not in PATH.")

# Download necessary NLTK data
nltk.download('punkt_tab', quiet=True) 
nltk.download('punkt', quiet=True)

app = FastAPI()

# Load URL detection model
try:
    url_model = joblib.load("model_url_v4.pkl")
    if not hasattr(url_model, 'predict'):
        raise ValueError(
            "Loaded URL model is not valid. Ensure it is a scikit-learn model or similar object with a 'predict' method. "
            "If the model file is invalid, retrain the model and save it using joblib or pickle."
        )
except Exception as e:
    raise RuntimeError(f"Failed to load model_url_v4.pkl: {str(e)}") from e

# Load SMS detection model
try:
    sms_model = joblib.load("sms_svm_model_v2.pkl")
    if not hasattr(sms_model, 'predict'):
        raise ValueError("Loaded SMS model is not valid. Ensure it has a 'predict' method.")
except Exception as e:
    raise RuntimeError(f"Failed to load model_sms_v2.pkl: {str(e)}") from e

class URLRequest(BaseModel):
    url: str

class SMSRequest(BaseModel):
    message: str

@app.post("/predict_url")
async def predict_url(request: URLRequest):
    try:
        feature_extractor = FeatureExtraction(request.url)
        features = feature_extractor.getFeaturesList()
        
        # Ensure features is a 2D array
        features_2d = [features]
        raw_pred = url_model.predict(features_2d)[0]
        prediction = int(raw_pred)
        
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
        sms_message_clean = preprocess_text(sms_message)
        sms_pred_int = int(sms_model.predict([sms_message_clean])[0])  # 0 = unsafe, 1 = safe

        # Look for URLs
        url_regex = r'(https?://\S+|www\.\S+)'  
        urls = re.findall(url_regex, sms_message)

        # Default “no URL” to safe
        url_pred_int = 1
        if urls:
            url = urls[0]
            feature_extractor = FeatureExtraction(url)
            features = feature_extractor.getFeaturesList()
            url_pred_int = int(url_model.predict([features])[0])

        # Final: safe only if both are safe
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
# from ollama_client import query_ollama
# from translation_utils import detect_language, translate_text

# @app.post("/chat")
# async def chat_endpoint(request: ChatRequest):
#     try:
#         input_lang = await detect_language(request.question)
        
#         # Ensure history exists, even if empty
#         history = request.history if hasattr(request, 'history') else []
        
#         if input_lang == "ar":
#             new_q_en = await translate_text(request.question, "en")
#         else:
#             new_q_en = request.question

#         english_response = await asyncio.to_thread(
#             chat_with_ollama,
#             history,  # Pass the possibly empty history
#             new_q_en
#         )

    #     if input_lang == "ar":
    #         final = await translate_text(english_response, "ar")
    #     else:
    #         final = english_response

    #     return {"response": final}
    # except Exception as e:
    #     if isinstance(e, AttributeError):
    #         raise HTTPException(status_code=400, detail="Invalid request format")
    #     raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80)


