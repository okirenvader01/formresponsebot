import requests


class OllamaClient:
    """
    Client for generating synthetic survey text using Ollama.
    """

    def __init__(
        self,
        base_url="http://localhost:11434",
        model="llama3.2:3b"
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def is_available(self):
        """
        Check whether Ollama is running and the requested model
        is available.
        """

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )

            if response.status_code != 200:
                return False

            data = response.json()

            models = data.get("models", [])

            for model in models:
                if model.get("name") == self.model:
                    return True

            return False

        except requests.RequestException:
            return False

    def generate(
        self,
        prompt,
        temperature=0.8,
        top_p=0.9
    ):
        """
        Generate text using the configured Ollama model.
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p
            }
        }

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "").strip()