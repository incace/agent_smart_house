from sklearn.preprocessing import MinMaxScaler


class Normalizer:
    BENEFIT_CRITERIA = [
        "context",
        "agent_score"
    ]

    COST_CRITERIA = [
        "input_price",
        "parameters"
    ]

    CRITERIA = BENEFIT_CRITERIA + COST_CRITERIA

    def validate(self, df):
        df = df.drop_duplicates(subset="model").copy()
        df = df.dropna(subset=self.CRITERIA)
        return df

    def normalize(self, df):
        df = self.validate(df).copy()

        scaler = MinMaxScaler()
        df[self.CRITERIA] = scaler.fit_transform(
            df[self.CRITERIA]
        )

        for criterion in self.COST_CRITERIA:
            df[criterion] = 1 - df[criterion]

        return df