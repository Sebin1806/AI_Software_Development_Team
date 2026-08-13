import logging
import ollama
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:

    @classmethod
    def get_client(cls) -> ollama.Client:
        return ollama.Client(
            host=settings.OLLAMA_BASE_URL,
            timeout=settings.OLLAMA_TIMEOUT,
        )

    @classmethod
    def generate(
        cls,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        mock_mode: bool = None,
    ) -> str:
        use_mock = settings.LLM_MOCK_MODE if mock_mode is None else mock_mode

        if use_mock:
            logger.info("LLMService generating response in MOCK mode.")
            return f"[MOCK AI RESPONSE]\nProcessed prompt:\n{prompt[:200]}..."

        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })
        messages.append({
            "role": "user",
            "content": prompt,
        })

        model_name = settings.OLLAMA_MODEL

        try:
            logger.info(f"Sending request to Ollama model '{model_name}' at '{settings.OLLAMA_BASE_URL}'")
            client = cls.get_client()
            response = client.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": temperature,
                }
            )

            if isinstance(response, dict):
                return response.get("message", {}).get("content", "")
            return response.message.content

        except Exception as e:
            err_msg = str(e)
            logger.error(f"Error calling Ollama service: {err_msg}")
            friendly_msg = (
                f"Ollama LLM Generation Failed: {err_msg}\n"
                f"-> Ensure Ollama service is running at '{settings.OLLAMA_BASE_URL}'.\n"
                f"-> Ensure required model '{model_name}' is installed by running: ollama run {model_name}\n"
                f"-> Alternatively, set LLM_MOCK_MODE=true in backend/.env to run in test mock mode."
            )
            raise RuntimeError(friendly_msg) from e