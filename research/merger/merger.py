from research.loaders.huggingface_loader import HuggingFaceLoader
from research.loaders.routerai_loader import RouterAILoader


class Merger:

    def merge(self):
        router_loader = RouterAILoader()
        router_df = router_loader.load()
        hf_loader = HuggingFaceLoader()
        hf_df = hf_loader.load(router_df["model"].tolist())
        models = router_df.merge(
            hf_df,
            on="model",
            how="left"
        )
        return models
