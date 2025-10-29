import argparse
import requests
import json

def query_model(prompt, model, host, port, stream=False):
    """Sends a query to the model via Ollama API."""
    api_url = f"http://{host}:{port}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response received.")
    except requests.exceptions.RequestException as e:
        return f"Request error: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the model via Ollama API.")
    parser.add_argument("--prompt", required=True, help="The prompt text to send to the model.")
    parser.add_argument("--model", required=True, help="The model name to use.")
    parser.add_argument("--host", required=False, default="127.0.0.1", help="The host where Ollama API is running.")
    parser.add_argument("--port", required=False, default="11434", help="The port on which Ollama API is listening.")
    parser.add_argument("--stream", action="store_true", help="Enable streaming response (default: False).")
    
    args = parser.parse_args()
    
    response = query_model(args.prompt, args.model, args.host, args.port, args.stream)
    print("Model Response:\n", response)