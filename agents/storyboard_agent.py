import json
from pathlib import Path
from typing import Any, List, Optional
import time
import requests
from requests.exceptions import ReadTimeout, ConnectionError, RequestException

from config.llm_config import LLMConfig

from langchain_core.outputs import Generation, LLMResult
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.llm import LLMChain
from langchain_core.language_models.llms import BaseLLM

class OllamaLLM(BaseLLM):
    @property
    def lc_type(self) -> str:
        return "ollama"

    def _call(self, prompt: str, stop=None) -> str:
        llm_config = LLMConfig()
        url = f"{llm_config.ollama_base_url}/api/generate"

        payload = {
            "model": llm_config.ollama_model,
            "prompt": prompt,
            "max_tokens": 500
        }

        max_retries = max(1, llm_config.ollama_max_retries)
        timeout = llm_config.ollama_timeout
        attempt = 0
        while True:
            try:
                response = requests.post(url, json=payload, stream=True, timeout=timeout)
                response.raise_for_status()
                break
            except ReadTimeout:
                attempt += 1
                if attempt >= max_retries:
                    raise RuntimeError(f"Read timed out while contacting Ollama at {url}. Increase OLLAMA_TIMEOUT or check the Ollama server.") from None
                time.sleep(2 ** attempt)
            except ConnectionError:
                raise RuntimeError(f"Connection error when contacting Ollama at {url}. Is the server running and reachable at {llm_config.ollama_base_url}?") from None
            except RequestException as e:
                raise RuntimeError(f"Error contacting Ollama: {e}") from e

        output = []
        try:
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if "response" in obj:
                        output.append(obj["response"])
                    if obj.get("done"):
                        break
                except Exception:
                    pass
        except ReadTimeout:
            raise RuntimeError(f"Read timed out while streaming response from Ollama at {url}. Increase OLLAMA_TIMEOUT or check server.") from None

        return "".join(output)

    @property
    def _llm_type(self) -> str:
        return "ollama"

    @property
    def _identifying_params(self):
        return {}

    def _generate(self, prompts, **kwargs):
        return LLMResult(
            generations=[[Generation(text=self._call(p))] for p in prompts]
        )

class APIBasedLLM(BaseLLM):
    @property
    def lc_type(self) -> str:
        return "api"

    def _call(self, prompt: str, stop=None) -> str:
        import openai

        llm_config = LLMConfig()
        openai.api_key = llm_config.api_key

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        return response.choices[0].message["content"]

    @property
    def _llm_type(self) -> str:
        return "api"

    @property
    def _identifying_params(self):
        return {}

    def _generate(self, prompts, **kwargs):
        return LLMResult(
            generations=[[Generation(text=self._call(p))] for p in prompts]
        )

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "storyboard_prompt.txt"
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    STORYBOARD_PROMPT = f.read()


class StoryboardAgent:
    def __init__(self):
        self.llm_config = LLMConfig()

    def generate_storyboard(self, transcript: str) -> dict:
        llm = APIBasedLLM() if self.llm_config.use_api else OllamaLLM()

        safe_prompt = STORYBOARD_PROMPT.replace("{", "{{").replace("}", "}}")
        prompt = PromptTemplate(
            template=safe_prompt + "\n\nTranscript:\n{transcript}",
            input_variables=["transcript"]
        )

        chain = prompt | llm
        result = chain.invoke({"transcript": transcript})

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "title": "Generated Storyboard",
                "scenes": [
                    {
                        "id": 1,
                        "description": result,
                        "actions": []
                    }
                ]
            }


    def save_storyboard(self, storyboard: dict, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(storyboard, f, indent=2)
