# IBM Granite Client for Existing OpenAI Applications

This Python library is an openai compatible ibm granite client. It simplifies integrating the IBM Granite language model into applications currently using the OpenAI API. It mimics the OpenAI API structure for a smoother transition.

## Usage

### Prerequisites

An IBM Cloud account with access to the IBM Watson Natural Language Understanding service and the Granite model. Just add the granite.py file to your project.

## Features

* **Simplified API:**  Uses an OpenAI-like API structure for easier integration if you're already familiar with OpenAI's libraries.
* **Automatic Token Refresh:** The client automatically refreshes the access token when it expires, ensuring uninterrupted operation.  This handles the common 401 (Unauthorized) error gracefully.
* **Error Handling:** Includes robust error handling for API requests, providing informative error messages.
* **IBM Granite-Specific Formatting:** Handles the differences in formatting between the OpenAI API style and the IBM Granite API.
### 1. Installation

```bash
pip install requests
```

### 2. Environment Variables

Before running, set these environment variables:

- `API_KEY`: Your IBM Cloud API key (from your IBM Cloud account).
- `PROJECT_ID`: Your IBM Granite project ID (from your IBM Watson project settings).

Eg: in Linux
```bash
export API_KEY="YOUR_API_KEY"
export PROJECT_ID="YOUR_PROJECT_ID"
```

### 3. Running the Code (`granite.py`)

The provided `granite.py` demonstrates usage:

```python
import os
from granite import IBMGraniteClient

client = IBMGraniteClient(
    api_key=os.getenv("API_KEY"),
    project_id=os.getenv("PROJECT_ID")
)

response = client.chat_completions_create(
    model="ibm/granite-3-8b-instruct",  # Or another Granite model ID
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant"},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    max_tokens=100
)

print(response['choices'][0]['message']['content'])
```

This sends a message to Granite and prints the response. The `messages` parameter uses the OpenAI API format.

### 4. Key Methods (`granite.py`)

- **`IBMGraniteClient(api_key, project_id)`**: Creates a client instance.
- **`chat_completions_create(model, messages, max_tokens, temperature, **kwargs)`**: Generates text completions. Mirrors OpenAI's `chat.completions.create`. Handles token refresh automatically.
  - `model`: Granite model ID (e.g., `"ibm/granite-3-8b-instruct"`).
  - `messages`: Conversation history (OpenAI format).
  - `max_tokens`: Maximum tokens to generate.
  - `temperature`: Controls randomness.
  - `**kwargs`: Additional parameters (not fully documented in provided code).

### 5. Integration with Existing OpenAI Applications

This library's main benefit is its OpenAI API compatibility. Replacing OpenAI calls with this Granite client often requires minimal code changes. Just swap the client and adjust model IDs.

### 6. Error Handling

The client handles token refresh failures (HTTP 401) and other API errors. Specific error messages are not fully detailed in this version of the code.

## Example of Migration (Illustrative)

Replacing an OpenAI call:

```python
openai.ChatCompletion.create(...)
```

With a Granite call:

```python
client.chat_completions_create(...)
```

Remember to install `requests`, set environment variables, and adjust parameters as needed. The provided code does not include detailed error handling or showcase all features of the underlying Granite API.

## Contributions Welcome!

