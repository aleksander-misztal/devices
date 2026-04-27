import json

from langfuse import get_client
from openai import OpenAI

from prompts.extract_specs import EXTRACT_SPECS_PROMPT
from settings import OPENAI_API_KEY, OPENAI_MODEL
from state import State

client = OpenAI(api_key=OPENAI_API_KEY)
langfuse = get_client()


def node_extract_specs(state: State) -> dict:
    with langfuse.start_as_current_observation(name="extract_specs", as_type="generation") as obs:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": EXTRACT_SPECS_PROMPT},
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
    specs = json.loads(content)
    # also surface brand/category as filters for downstream
    filters = {
        "brand": specs.get("brand"),
        "category": specs.get("category"),
    }
    return {"specs": specs, "filters": filters}
