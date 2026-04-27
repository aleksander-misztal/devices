import json

from langfuse import get_client
from openai import OpenAI

from prompts.extract import EXTRACT_SYSTEM_PROMPT
from settings import OPENAI_API_KEY, OPENAI_MODEL
from state import State

client = OpenAI(api_key=OPENAI_API_KEY)
langfuse = get_client()


def node_extract(state: State) -> dict:
    with langfuse.start_as_current_observation(name="extract", as_type="generation") as obs:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
                {"role": "user", "content": state["question"]},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = response.choices[0].message.content
        obs.update(
            model=OPENAI_MODEL,
            input=state["question"],
            output=content,
            usage_details={
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
            },
        )
    result = json.loads(content)
    return {"extracted_devices": result.get("devices", [])}
