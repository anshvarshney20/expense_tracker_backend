import json
import logging
from typing import Any, Optional
import google.generativeai as genai
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.exceptions import InternalServerError

logger = logging.getLogger(__name__)

class AIAnalysisResponse(BaseModel):
    summary: str
    savings_tip: str
    suggestions: list[dict[str, Any]]
    discipline_score: int
    savings_rate: float
    timeline_impact: str
    savings_potential: float
    risk_level: str

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-pro")
        else:
            self.model = None

    async def analyze_expenses(self, expenses_data: list[dict]) -> AIAnalysisResponse:
        if not self.model:
            # Mock response if no API key
            return AIAnalysisResponse(
                summary="AI Analysis is currently disabled (API Key missing).",
                savings_tip="Enable neural link (API Key) for predictive financial modeling.",
                suggestions=[{"category": "General", "reduction": 0, "reason": "Add API Key"}],
                discipline_score=0,
                savings_rate=0.0,
                timeline_impact="N/A",
                savings_potential=0.0,
                risk_level="Unknown"
            )

        prompt = f"""
        Analyze the following expense data and provide a structured JSON response.
        Data: {json.dumps(expenses_data)}
        
        Return JSON with fields:
        - summary: A human-readable summary of spending habits.
        - savings_tip: A single, punchy, high-impact sentence of advice.
        - suggestions: A list of 3 JSON objects with keys: category, reduction (float), reason.
        - discipline_score: A value from 0-100 reflecting budget adherence.
        - savings_rate: A float from 0-1 representing savings vs spending.
        - timeline_impact: A string describing how current spending affects goals.
        - savings_potential: Estimated monthly savings in numeric value.
        - risk_level: One of [Low, Medium, High].
        """

        try:
            # Note: This is a simplified call format for the skeleton
            response = await self._call_gemini(prompt)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"AI Service Error: {str(e)}")
            raise InternalServerError(message="Failed to process AI analysis")

    async def _call_gemini(self, prompt: str) -> str:
        # Simplified async call wrapper (genai's generate_content is blocking, 
        # normally would use run_in_executor or specialized async lib)
        # For production-ready skeleton, we show the retry/timeout logic
        import anyio
        
        retries = 3
        for i in range(retries):
            try:
                # Mocking async with anyio.to_thread for the prompt
                response = await anyio.to_thread.run_sync(self.model.generate_content, prompt)
                return response.text
            except Exception as e:
                if i == retries - 1:
                    raise e
                await anyio.sleep(1)
        return ""

    def _parse_response(self, text: str) -> AIAnalysisResponse:
        try:
            # Basic cleanup if GEMINI returns markdown code blocks
            clean_text = text.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_text)
            return AIAnalysisResponse(**data)
        except (ValueError, ValidationError) as e:
            logger.error(f"AI Parse Error: {str(e)} | Raw: {text}")
            raise InternalServerError(message="Invalid response from AI")
