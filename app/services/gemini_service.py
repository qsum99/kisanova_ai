import google.generativeai as genai
from app.config import GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("[gemini_service] Warning: GEMINI_API_KEY is not configured.")

def get_treatment_recommendation(disease_name: str) -> str:
    if not GEMINI_API_KEY:
        return (
            f"Disease detected: {disease_name}. "
            "(Gemini recommendations are currently disabled because the API key is missing.)"
        )
        
    prompt = (
        f"Provide exactly 3 short, actionable bullet points for treating the plant disease '{disease_name}'. "
        f"CRITICAL: Write in EXTREMELY simple, everyday language for a regular farmer. Do NOT use scientific or agricultural jargon like 'economic thresholds', 'registered insecticides', 'life cycles', or 'pathogens'. "
        f"Use simple words like 'Look for bugs', 'Spray bug killer if you see too many', 'Plant a different crop next season'. "
        f"Do not include any introductory text, background information, or full paragraphs. Just return the 3 simple bullet points."
    )
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text:
            return f"Disease detected: {disease_name}.\n\n{text}"
    except Exception as e:
        print(f"[gemini_service] Error calling Gemini API: {e}")
        
    return (
        f"Disease detected: {disease_name}. "
        "Please consult a local agricultural expert for specific treatment. "
        "General recommendations: remove affected leaves, ensure proper spacing "
        "for air circulation, and consider applying appropriate fungicides or pesticides."
    )
