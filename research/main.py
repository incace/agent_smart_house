import research.merger.merger as mg
import research.normalizer.normalizer as nm
import research.ranker.ranker as rk


def main():
    merger = mg.Merger()
    normalizer = nm.Normalizer()
    ranker = rk.Ranker()
    df = merger.merge()
    validated_df = normalizer.validate(df)
    normalized_df = normalizer.normalize(validated_df)
    final_df = ranker.calc_sum(normalized_df)
    print(final_df.head(5))


if __name__ == "__main__":
    main()

