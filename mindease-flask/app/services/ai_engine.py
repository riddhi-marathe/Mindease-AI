import os
from dotenv import load_dotenv

load_dotenv()


class AIEngine:
    """
    AI Engine using Google Gemini API for wellness recommendations
    and health insights based on user input
    """

    def __init__(self):
        try:
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-pro")
            self.available = True
        except Exception as e:
            print(f"Warning: AI Engine initialization failed: {e}")
            self.available = False

    def get_wellness_recommendations(
        self, symptoms: str, health_history: str, lifestyle: str
    ) -> str:
        """
        Generate wellness recommendations based on symptoms and health data
        """
        if not self.available:
            return "AI Engine not available. Please check your Google Gemini API key configuration in the .env file."

        try:
            import google.generativeai as genai
        except ImportError:
            return "AI Engine not available."

        prompt = f"""
        Based on the following information, provide personalized wellness recommendations:
        
        Symptoms: {symptoms}
        Health History: {health_history}
        Lifestyle: {lifestyle}
        
        Please provide:
        1. Initial assessment
        2. Recommended wellness practices
        3. When to seek professional help
        4. Preventive measures
        
        Keep the response concise and practical.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback mock response for demo purposes
            return """Thank you for sharing your health concerns. Here's some general wellness advice:

1. **Initial Assessment**: Based on what you've described, it's important to monitor your symptoms and maintain healthy habits.

2. **Recommended Wellness Practices**:
   - Stay hydrated and eat balanced meals
   - Get adequate sleep (7-9 hours per night)
   - Practice stress-reduction techniques like deep breathing or meditation
   - Maintain regular physical activity appropriate for your fitness level

3. **When to Seek Professional Help**: If symptoms persist, worsen, or you're concerned about your health, consult a healthcare provider.

4. **Preventive Measures**: Focus on preventive care through regular check-ups, healthy lifestyle choices, and early intervention when needed.

Remember, this is general advice. For personalized medical recommendations, please consult with a qualified healthcare professional."""

    def get_mental_health_support(
        self, mood: str, stressors: str, coping_methods: str
    ) -> str:
        """
        Generate mental health support and coping strategies
        """
        if not self.available:
            return "AI Engine not available. Please check your Google Gemini API key configuration in the .env file."

        prompt = f"""
        Based on the following mental health information, provide supportive guidance:
        
        Current Mood: {mood}
        Stressors: {stressors}
        Current Coping Methods: {coping_methods}
        
        Please provide:
        1. Validation and understanding
        2. Evidence-based coping strategies
        3. Mindfulness or relaxation techniques
        4. When to seek professional help
        
        Keep the response warm, supportive, and practical.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating support: {str(e)}"

    def analyze_health_metrics(self, metrics: dict) -> str:
        """
        Analyze health metrics and provide insights
        """
        if not self.available:
            return "AI Engine not available. Please check your Google Gemini API key configuration in the .env file."

        metrics_str = "\n".join([f"{k}: {v}" for k, v in metrics.items()])

        prompt = f"""
        Analyze the following health metrics and provide insights:
        
        {metrics_str}
        
        Please provide:
        1. Overall health assessment
        2. Metrics that need attention
        3. Positive indicators
        4. Recommended actions
        
        Be concise and practical.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error analyzing metrics: {str(e)}"
