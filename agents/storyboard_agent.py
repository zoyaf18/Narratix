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
        raw_result = chain.invoke({"transcript": transcript})

        # Extract text from various llm return types
        result_text = None
        if isinstance(raw_result, str):
            result_text = raw_result
        elif isinstance(raw_result, dict):
            for key in ("text", "content", "response", "output", "result"):
                if key in raw_result and isinstance(raw_result[key], str):
                    result_text = raw_result[key]
                    break
            if not result_text and "generations" in raw_result:
                try:
                    result_text = raw_result["generations"][0][0]["text"]
                except Exception:
                    pass
        else:
            # Try attribute access for common LLM return objects
            if hasattr(raw_result, "generations"):
                try:
                    gens = raw_result.generations
                    if isinstance(gens, list) and gens and isinstance(gens[0], list):
                        result_text = gens[0][0].text
                except Exception:
                    pass
            if not result_text and hasattr(raw_result, "text"):
                try:
                    result_text = raw_result.text
                except Exception:
                    pass

        if result_text is None:
            result_text = str(raw_result)

        # Try to parse JSON directly, then try extracting a JSON substring, else create a safe fallback
        storyboard = None
        try:
            storyboard = json.loads(result_text)
        except json.JSONDecodeError:
            # Attempt to extract the first balanced JSON object from the text
            start = result_text.find("{")
            if start != -1:
                count = 0
                for i in range(start, len(result_text)):
                    if result_text[i] == "{":
                        count += 1
                    elif result_text[i] == "}":
                        count -= 1
                        if count == 0:
                            candidate = result_text[start:i+1]
                            try:
                                storyboard = json.loads(candidate)
                                break
                            except json.JSONDecodeError:
                                # continue searching
                                continue

        if storyboard is None:
            # Build a schema-compliant fallback storyboard using the raw text as narration
            storyboard = {
                "title": "Generated Storyboard",
                "description": "Auto-generated fallback storyboard due to non-JSON model output",
                "scenes": [
                    {
                        "scene_id": 1,
                        "duration": 5,
                        "narration": result_text.strip(),
                        "animation_type": "text",
                        "elements": [
                            {
                                "type": "text",
                                "content": result_text.strip(),
                                "position": [0, 0],
                                "color": "WHITE",
                                "animation": "FadeIn",
                                "scale": 1.0
                            }
                        ]
                    }
                ]
            }

        # Normalize and validate minimal schema expectations
        def _normalize(sb: dict) -> dict:
            if not isinstance(sb, dict):
                return storyboard
            if "title" not in sb:
                sb["title"] = "Generated Storyboard"
            if "scenes" not in sb or not isinstance(sb["scenes"], list):
                sb["scenes"] = []

            normalized = []
            for idx, s in enumerate(sb["scenes"], start=1):
                if not isinstance(s, dict):
                    s = {"narration": str(s)}
                scene_id = s.get("scene_id") or s.get("id") or idx
                duration = s.get("duration", 5)
                narration = s.get("narration") or s.get("description") or s.get("text") or ""
                animation_type = s.get("animation_type") or s.get("type") or "text"

                elements = s.get("elements") or s.get("actions") or []
                normalized_elements = []
                for e in elements:
                    if isinstance(e, str):
                        normalized_elements.append({
                            "type": "text",
                            "content": e,
                            "position": [0, 0],
                            "color": "WHITE",
                            "animation": "FadeIn",
                            "scale": 1.0
                        })
                        continue
                    if not isinstance(e, dict):
                        continue
                    normalized_elements.append({
                        "type": e.get("type", "text"),
                        "content": e.get("content", ""),
                        "position": e.get("position", [0, 0]),
                        "color": e.get("color", "WHITE"),
                        "animation": e.get("animation", "FadeIn"),
                        "scale": e.get("scale", 1.0)
                    })

                normalized.append({
                    "scene_id": int(scene_id),
                    "duration": duration,
                    "narration": narration,
                    "animation_type": animation_type,
                    "elements": normalized_elements
                })

            sb["scenes"] = normalized
            return sb

        storyboard = _normalize(storyboard)
        return storyboard


    def save_storyboard(self, storyboard: dict, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(storyboard, f, indent=2)
