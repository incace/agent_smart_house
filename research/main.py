import research.merger.merger as mg
import research.ranker.ranker as rk


def main():
    df = mg.merge()
    ranker = rk.Ranker()
    final_df = ranker.rank_by_topsis(df)
    print(final_df.head(5))


if __name__ == "__main__":
    main()

