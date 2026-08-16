import os

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


class LLM:

    def __init__(self, model):
        self.model = model
        self.client = OpenAI(
            api_key=os.getenv(
                "OPENROUTER_API_KEY"
            ),
            base_url=
            "https://openrouter.ai/api/v1",
            timeout=120
        )

    def ask(self, messages, config, tools):
        response = self.client.chat.completions.create(

            model=self.model,

            messages=messages,

            temperature=
            config["generation"]["temperature"],

            top_p=
            config["generation"]["top_p"],

            max_tokens=
            config["generation"]["num_predict"],

            tools=tools

        )

        return response.choices[0].message


