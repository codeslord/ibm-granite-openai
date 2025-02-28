import os
import requests
import time
from typing import List, Dict, Optional

class IBMGraniteClient:
    def __init__(self, api_key: str, project_id: str):
        self.api_key = api_key
        self.project_id = project_id
        self.access_token = None
        self.base_url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
        self._refresh_token()  # Initial token fetch

    def _refresh_token(self):
        """Refresh the access token"""
        url = 'https://iam.cloud.ibm.com/identity/token'
        data = {
            'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
            'apikey': self.api_key
        }

        response = requests.post(url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=data)
        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")

        self.access_token = response.json()['access_token']

    @staticmethod
    def _format_messages(messages: List[Dict]) -> str:
        """Convert OpenAI-style messages to IBM format"""
        formatted = ""
        for msg in messages:
            role = msg['role'] if msg['role'] != 'system' else 'system'
            formatted += f"<|start_of_role|>{role}<|end_of_role|>{msg['content']}<|end_of_text|>\n"
        return formatted + "<|start_of_role|>assistant<|end_of_role|>"

    def chat_completions_create(
        self,
        model: str = "ibm/granite-3-8b-instruct",
        messages: List[Dict] = None,
        max_tokens: int = 900,
        temperature: float = 1.0,
        **kwargs
    ) -> Dict:
        """OpenAI-style completion method with automatic token refresh on 401 errors"""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        body = {
            "input": self._format_messages(messages),
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": max_tokens,
                "min_new_tokens": 0,
                "repetition_penalty": temperature,
                **kwargs
            },
            "model_id": model,
            "project_id": self.project_id
        }

        response = requests.post(self.base_url, headers=headers, json=body)
        
        # Handle token expiration specifically
        if response.status_code == 401:
            try:
                error_data = response.json()
                if any(error.get('code') == 'authentication_token_not_valid' 
                       for error in error_data.get('errors', [])):
                    self._refresh_token()
                    headers['Authorization'] = f"Bearer {self.access_token}"
                    response = requests.post(self.base_url, headers=headers, json=body)
            except requests.exceptions.JSONDecodeError:
                pass  # If we can't parse the error, continue to raise

        if response.status_code != 200:
            raise Exception(f"API Error ({response.status_code}): {response.text}")

        return self._format_response(response.json())

    @staticmethod
    def _format_response(ibm_response: Dict) -> Dict:
        """Format IBM response to OpenAI-style format"""
        return {
            "id": f"ibm_{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": ibm_response.get('model_id', 'ibm-model'),
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": ibm_response['results'][0]['generated_text']
                },
                "finish_reason": "stop",
                "index": 0
            }],
            "usage": {
                "prompt_tokens": 0,  # IBM doesn't provide token counts
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }

if __name__ == "__main__":
    client = IBMGraniteClient(
        api_key=os.getenv("API_KEY"),
        project_id=os.getenv("PROJECT_ID")
    )

    response = client.chat_completions_create(
        model="ibm/granite-3-8b-instruct",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant"},
            {"role": "user", "content": "What is the capital of France?"}
        ],
        max_tokens=100
    )

    print(response['choices'][0]['message']['content'])