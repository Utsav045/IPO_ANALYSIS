from django.shortcuts import render
from django.http import JsonResponse

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize API clients
try:
    # OpenAI client (existing)
    from openai import OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)
    else:
        openai_client = None
except Exception as e:
    openai_client = None
    print(f"OpenAI initialization error: {e}")


try:
    # Gemini client (new)
    import google.generativeai as genai
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key and gemini_api_key != "YOUR_GEMINI_API_KEY_HERE":
        genai.configure(api_key=gemini_api_key)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        gemini_model = None
except Exception as e:
    gemini_model = None
    print(f"Gemini initialization error: {e}")

def home(request):
    upcoming_ipos = [
        {"name": "TechNova Ltd", "open": "10 Sept", "close": "12 Sept", "price_band": "₹120 - ₹130"},
        {"name": "GreenEnergy Corp", "open": "14 Sept", "close": "16 Sept", "price_band": "₹250 - ₹270"},
    ]

    ongoing_ipos = [
        {"name": "FinTech Solutions", "close": "7 Sept", "price_band": "₹500 - ₹520"},
    ]

    past_ipos = [
        {"name": "HealthPlus Pharma", "close": "25 Aug", "listed": "₹310 (10% gain)"},
        {"name": "EduGrow Tech", "close": "18 Aug", "listed": "₹95 (−5% drop)"},
    ]

    context = {
        "upcoming_ipos": upcoming_ipos,
        "ongoing_ipos": ongoing_ipos,
        "past_ipos": past_ipos,
    }
    return render(request, "ipo_app/index.html", context)

def get_response(request):
    user_message = request.GET.get('message', '')
    
    # Determine which API to use (default to Gemini if available)
    use_gemini = gemini_model is not None
    
    try:
        if use_gemini:
            # Use Gemini API
            if not gemini_api_key or gemini_api_key == "YOUR_GEMINI_API_KEY_HERE":
                bot_response = "⚠️ Gemini API key not configured. Please set GEMINI_API_KEY in .env file."
            else:
                # Generate response using Gemini with structured format request
                prompt = f"""You are Nexa AI, a friendly chatbot specialized in IPO analysis. 
                Please provide your response in a structured format with clear sections when appropriate.
                For IPO-related queries, organize information in sections like:
                - Company Overview
                - Financial Highlights
                - Risk Factors
                - Recommendation
                
                Respond to the following query: {user_message}"""
                response = gemini_model.generate_content(prompt)
                bot_response = response.text.strip()
        else:
            # Fallback to OpenAI API
            if not openai_client:
                bot_response = "⚠️ No API key configured. Please set either OPENAI_API_KEY or GEMINI_API_KEY in .env file."
            else:
                # Call OpenAI API with structured format request
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": """You are Nexa AI, a friendly chatbot specialized in IPO analysis.
                        Please provide your response in a structured format with clear sections when appropriate.
                        For IPO-related queries, organize information in sections like:
                        - Company Overview
                        - Financial Highlights
                        - Risk Factors
                        - Recommendation"""},
                        {"role": "user", "content": user_message}
                    ]
                )
                bot_response = response.choices[0].message.content.strip()

    except Exception as e:
        bot_response = f"⚠️ Error: {str(e)}"

    return JsonResponse({"response": bot_response})