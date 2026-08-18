class Ranker:
    WEIGHTS = {
        "input_price": 0.40,
        "agent_score": 0.35,
        "context": 0.15,
        "parameters": 0.10,
    }

    def calc_sum(self, df):
        df = df.copy()

        df["score"] = sum(
            df[criterion] * weight
            for criterion, weight in self.WEIGHTS.items()
        )

        return df.sort_values(
            by="score",
            ascending=False
        )