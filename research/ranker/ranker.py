import numpy as np
from ..normalizer import normalizer


class Ranker:
    WEIGHTS = {
        "input_price": 0.40,
        "agent_score": 0.35,
        "context": 0.15,
        "parameters": 0.10,
    }

    BENEFIT_CRITERIA = [
        "context",
        "agent_score"
    ]

    COST_CRITERIA = [
        "input_price",
        "parameters"
    ]

    CRITERIA = (
        BENEFIT_CRITERIA +
        COST_CRITERIA
    )

    def rank_by_topsis(self, df):
        df = df.copy()
        validated_df = normalizer.validate(df, self.CRITERIA)
        normalized_df = normalizer.normalize(validated_df, self.CRITERIA)

        for criterion, weight in self.WEIGHTS.items():
            normalized_df[criterion] *= weight

        ideal = {}
        anti_ideal = {}

        for criterion in self.CRITERIA:

            if criterion in self.BENEFIT_CRITERIA:
                ideal[criterion] = normalized_df[criterion].max()
                anti_ideal[criterion] = normalized_df[criterion].min()

            else:
                ideal[criterion] = normalized_df[criterion].min()
                anti_ideal[criterion] = normalized_df[criterion].max()

        distance_to_ideal = np.sqrt(
            sum(
                (normalized_df[criterion] - ideal[criterion]) ** 2
                for criterion in self.CRITERIA
            )
        )

        distance_to_anti_ideal = np.sqrt(
            sum(
                (normalized_df[criterion] - anti_ideal[criterion]) ** 2
                for criterion in self.CRITERIA
            )
        )

        df["score"] = (
            distance_to_anti_ideal /
            (
                distance_to_ideal +
                distance_to_anti_ideal
            )
        )

        return df.sort_values(
            by="score",
            ascending=False
        )

