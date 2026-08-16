from sklearn.preprocessing import MinMaxScaler


class Normalizer:
    CRITERIA = [
        "input_price",
        "context",
        "parameters",
        "agent_score"
    ]

    def validate(self, df):
        df = df.drop_duplicates(subset="model")
        df = df.dropna(subset=["parameters"])
        return df

    def normalize(self, df):
        validated_df = self.validate(df)
        scaler = MinMaxScaler()
        validated_df[self.CRITERIA] = scaler.fit_transform(validated_df[self.CRITERIA])
        return validated_df


