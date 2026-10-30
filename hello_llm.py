import os

from dotenv import load_dotenv
from openai import OpenAI
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    RateLimitError,
)

# Load local environment variables
load_dotenv()

# Create an OpenAI API client
client = OpenAI()

# Define a simulated API failure
failure = """
Endpoint: Get /api/users/123
Expected status: 200
Actual status: 500
Response body:
{"error": "Internal Server Error"}
"""

# Step 1: Send API request
try:
    response = client.responses.create(
        model = os.environ["OPENAI_MODEL"],
        instructions= (
            "You are a backend debugging assistant." 
            "Distinguish observed facts from hypotheses."
            "Do not claim a root cause without evidence."
        ),
        input = (
            "Analyze this API failure. "
            "Give two possible causes and one next debugging step. \n\n"
            f"{failure}"
        ),
        max_output_tokens = 500,
)

# Step 2: Handle API errors
except RateLimitError as e:
    print("HTTP 429: Rate limit or insufficient credits.")
    print("Details:", e)
    raise SystemExit(1) from None

except APITimeoutError:
    print("The API request timed out.")
    raise SystemExit(1) from None

except APIConnectionError:
    print("Could not connect to the OpenAI API.")
    raise SystemExit(1) from None

except APIStatusError as e:
    print(f"API returned HTTP {e.status_code}.")
    raise SystemExit(1) from None

# Step 3: Validate the response
if response.status != "completed":
    print("Response did not complete:", response.status)
    print("Incomplete details:", response.incomplete_details)
    raise SystemExit(1)


# Step 4: Process the response
print("=== DevLens Investigation ===")
print(response.output_text)

# Step 5: Inspect metadata
print("\n=== Response Metadata ===")
print("Response ID:", response.id)
print("Status:", response.status)

print("\n=== Output Item Types ===")
for item in response.output:
    print(item.type)

# Step 6: Inspect token usage
if response.usage is not None:
    print("\n=== Token Usage ===")
    print("Input tokens:", response.usage.input_tokens)
    print("Output tokens:", response.usage.output_tokens)
    print("Total tokens:", response.usage.total_tokens)

    if response.usage.output_tokens_details is not None:
        print(
            "Reasoning tokens:",
            response.usage.output_tokens_details.reasoning_tokens
        )