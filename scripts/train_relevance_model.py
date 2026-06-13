"""Train LightGBM relevance ranker from synthetic/heuristic labels."""

from __future__ import annotations

from services.agents.relevance_model import RelevanceFeatures, train_model

# Starter training set derived from graph-path intuition; replace with feedback labels in prod.
FEATURE_ROWS = [
    RelevanceFeatures(0, 0.95, 1, 1.0, 1.0).as_list(),
    RelevanceFeatures(1, 0.85, 1, 0.85, 1.0).as_list(),
    RelevanceFeatures(2, 0.70, 2, 0.7, 0.8).as_list(),
    RelevanceFeatures(3, 0.55, 1, 0.55, 0.5).as_list(),
    RelevanceFeatures(3, 0.50, 1, 0.4, 0.3).as_list(),
]
LABELS = [1, 1, 1, 0, 0]


def main() -> None:
    path = train_model(FEATURE_ROWS, LABELS)
    print(f"Model saved to {path}")


if __name__ == "__main__":
    main()
