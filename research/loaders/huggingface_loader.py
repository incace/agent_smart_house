from huggingface_hub import HfApi
import re
import pandas as pd


class HuggingFaceLoader:

    def __init__(self):
        self.api = HfApi()

    def load(self, model_ids):
        rows = []

        for model_id in model_ids:
            parameters = self.extract_params(model_id)
            if parameters:
                rows.append({
                    "model": model_id,
                    "parameters": parameters
                })
        return pd.DataFrame(rows)

    def extract_params(self, model_id):
        match = re.search(r"(\d+(\.\d+)?)B", model_id, re.IGNORECASE)

        if match:
            return float(match.group(1)) * 1e9

        return None
