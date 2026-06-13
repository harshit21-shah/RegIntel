"""LightGBM relevance ranker over graph-path features."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

MODEL_PATH = Path("data/models/relevance_lgbm.txt")


@dataclass(frozen=True)
class RelevanceFeatures:
    hop_count: int
    base_score: float
    matched_category_count: int
    weight_multiplier: float
    jurisdiction_match: float

    def as_list(self) -> list[float]:
        return [
            float(self.hop_count),
            self.base_score,
            float(self.matched_category_count),
            self.weight_multiplier,
            self.jurisdiction_match,
        ]


class RelevanceRanker:
    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        self.model_path = model_path
        self._model: object | None = None
        if model_path.exists():
            try:
                import lightgbm as lgb

                self._model = lgb.Booster(model_file=str(model_path))
                logger.info("Loaded LightGBM relevance model from %s", model_path)
            except Exception:
                logger.warning("Failed to load LightGBM model", exc_info=True)

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def score(self, features: RelevanceFeatures) -> float:
        if self._model is not None:
            import numpy as np

            booster = self._model
            raw = booster.predict(np.array([features.as_list()]))  # type: ignore[attr-defined]
            return float(max(0.0, min(1.0, raw[0])))

        combined = (
            features.base_score * 0.4
            + features.weight_multiplier * 0.3
            + features.jurisdiction_match * 0.1
            + min(1.0, features.matched_category_count / 3.0) * 0.2
        )
        return max(0.05, min(1.0, combined))


def train_model(
    feature_rows: list[list[float]],
    labels: list[int],
    *,
    output_path: Path = MODEL_PATH,
) -> Path:
    import lightgbm as lgb
    import numpy as np

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset = lgb.Dataset(np.array(feature_rows), label=np.array(labels))
    params = {
        "objective": "binary",
        "metric": "auc",
        "verbosity": -1,
        "num_leaves": 8,
        "learning_rate": 0.1,
    }
    model = lgb.train(params, dataset, num_boost_round=50)
    model.save_model(str(output_path))
    logger.info("Saved relevance model to %s", output_path)
    return output_path
