import os

from dotenv import load_dotenv

# Load variables from the local .env file
load_dotenv()

# Read configuration values
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

# Validate configuration without exposing secrets
if not api_key or api_key == "your_actual_api_key_here":
    raise RuntimeError("OPENAI_API_KEY is not configured")

if not model:
    raise RuntimeError("OPENAI_MODEL is not configured")

print("API Key configured:", True)
print("Selected model:", model)
print("Configuration check passed!")
