import numpy as np


def validate(df, criteria):
    df = df.drop_duplicates(subset="model").copy()
    df = df.dropna(subset=criteria)
    return df


def normalize(df, criteria):
    df = validate(df, criteria).copy()

    for criterion in criteria:
        denominator = np.sqrt(
            (df[criterion] ** 2).sum()
        )

        if denominator == 0:
            df[criterion] = 0
        else:
            df[criterion] = (df[criterion] / denominator)
    return df

