from app.services.llm_service import LLMService

prompt = """
You are a Project Manager AI agent.

Explain in 3 short points what a software development
project manager should do.
"""

print("--- Testing Mock Mode ---")
mock_response = LLMService.generate(prompt, mock_mode=True)
print("MOCK RESPONSE:\n", mock_response)
assert "[MOCK AI RESPONSE]" in mock_response

print("\n--- Testing Live Ollama Mode ---")
try:
    live_response = LLMService.generate(prompt, mock_mode=False)
    print("LIVE AI RESPONSE:\n", live_response)
except Exception as e:
    print("Live Ollama call returned error (Ollama service may be offline or model pulling):", e)