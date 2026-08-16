class Ranker:
    WEIGHTS = {
        "input_price": 0.40,
        "agent_score": 0.35,
        "context": 0.15,
        "parameters": 0.10,
    }

    def inv_criteria(self, normalized_df, column_id):
        normalized_df[column_id] = 1 - normalized_df[column_id]
        return normalized_df

    def calc_sum(self, df):
        df = self.inv_criteria(df, "input_price")
        df = self.inv_criteria(df, "parameters")

        df["score"] = (
            df["input_price"] * self.WEIGHTS["input_price"] +
            df["agent_score"] * self.WEIGHTS["agent_score"] +
            df["context"] * self.WEIGHTS["context"] +
            df["parameters"] * self.WEIGHTS["parameters"]
        )

        return df.sort_values(
            by="score",
            ascending=False
        )
