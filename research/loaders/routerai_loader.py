import requests
import pandas as pd


class RouterAILoader:

    URL = "https://routerai.ru/api/v1/models?input_modalities[]=text"

    OPEN_MODELS = (
        "qwen/",
        "meta-llama/",
        "google/",
        "mistralai/",
        "deepseek/",
        "microsoft/",
        "tiiuae/",
    )

    AGENT_WEIGHTS = {
        "tools": 0.35,
        "tool_choice": 0.15,
        "structured_outputs": 0.20,
        "response_format": 0.10,
        "reasoning": 0.10,
        "include_reasoning": 0.10,
        "seed": 0.05,
        "temperature": 0.05,
    }

    def load(self):
        response = requests.get(self.URL)
        response.raise_for_status()

        models = response.json()["data"]

        return self.process(models)

    def process(self, models):

        df = pd.json_normalize(models)

        df["agent_score"] = df["supported_parameters"].apply(
            self.calculate_agent_score
        )

        df = df[
            [
                "id",
                "context_length",
                "pricing.prompt",
                "pricing.completion",
                "architecture.input_modalities",
                "architecture.output_modalities",
                "agent_score"
            ]
        ]

        df = df.rename(columns={
            "id": "model",
            "context_length": "context",
            "pricing.prompt": "input_price",
            "pricing.completion": "output_price",
            "architecture.input_modalities": "input_modalities",
            "architecture.output_modalities": "output_modalities"
        })

        return df[df["model"].str.startswith(self.OPEN_MODELS)]

    def calculate_agent_score(self, parameters):
        if not isinstance(parameters, list):
            return 0.0

        return min(
            sum(self.AGENT_WEIGHTS.get(p, 0.0) for p in parameters),
            1.0
        )
