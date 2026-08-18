import numpy as np


class Ranker:
    WEIGHTS = {
        "input_price": 0.40,
        "agent_score": 0.35,
        "context": 0.15,
        "parameters": 0.10,
    }

    CRITERIA = {
        "input_price": "cost",
        "agent_score": "benefit",
        "context": "benefit",
        "parameters": "cost",
    }

    def topsis(self, df):
        df = df.copy()

        criteria = list(self.WEIGHTS.keys())

        normalized = df[criteria].copy()

        for column in criteria:
            denominator = np.sqrt(
                (normalized[column] ** 2).sum()
            )

            normalized[column] /= denominator

        weighted = normalized.copy()

        for column, weight in self.WEIGHTS.items():
            weighted[column] *= weight

        ideal = {}
        anti_ideal = {}

        for column in criteria:
            if self.CRITERIA[column] == "benefit":
                ideal[column] = weighted[column].max()
                anti_ideal[column] = weighted[column].min()
            else:
                ideal[column] = weighted[column].min()
                anti_ideal[column] = weighted[column].max()

        distance_ideal = np.sqrt(
            sum(
                (weighted[column] - ideal[column]) ** 2
                for column in criteria
            )
        )

        distance_anti = np.sqrt(
            sum(
                (weighted[column] - anti_ideal[column]) ** 2
                for column in criteria
            )
        )

        df["score"] = (
            distance_anti /
            (distance_ideal + distance_anti)
        )

        return df.sort_values(
            by="score",
            ascending=False
        )
