"""
Support Ticket Automation System
Machine Learning Classification Service

Uses scikit-learn TfidfVectorizer + LogisticRegression baseline with reproducible seed.
Classifies customer support messages into 4 categories:
1. Billing
2. Technical
3. Access
4. General

NOTE: Model confidence scores represent calibrated model probability estimates,
NOT guaranteed correctness. Low confidence or ambiguous multi-domain queries
are flagged for human review.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np

logger = logging.getLogger("app.classifier")

# Documented confidence threshold for human triage.
# In a 4-class space (uniform random baseline = 0.25):
# A threshold of 0.40 requires substantially higher probability than random chance.
# A margin of 0.10 ensures clear distinction between the top-ranked and runner-up categories.
UNCERTAINTY_CONFIDENCE_THRESHOLD = 0.40
UNCERTAINTY_MARGIN_THRESHOLD = 0.10

SUPPORTED_CATEGORIES = ["Billing", "Technical", "Access", "General"]


class TicketClassifier:
    """
    Lightweight, reproducible scikit-learn text classifier for support tickets.
    """

    def __init__(self, data_path: Optional[str] = None):
        self.model: Optional[Pipeline] = None
        self.categories: List[str] = SUPPORTED_CATEGORIES
        self.is_trained: bool = False

        # Resolve path to sample_data/train.json
        if data_path:
            self.data_path = Path(data_path)
        else:
            base_dir = Path(__file__).resolve().parent.parent
            self.data_path = base_dir / "sample_data" / "train.json"

        self._initialize_and_train()

    def _initialize_and_train(self) -> None:
        """
        Builds the TF-IDF + Logistic Regression pipeline and trains on train.json.
        """
        try:
            if not self.data_path.exists():
                logger.error(f"Training dataset not found at {self.data_path}")
                self.is_trained = False
                return

            with open(self.data_path, "r", encoding="utf-8") as f:
                records = json.load(f)

            if not records:
                logger.error("Training dataset is empty.")
                self.is_trained = False
                return

            texts = [r["message"] for r in records]
            labels = [r["category"] for r in records]

            # Build pipeline with n-gram features (unigrams & bigrams)
            self.model = Pipeline([
                (
                    "tfidf",
                    TfidfVectorizer(
                        ngram_range=(1, 2),
                        lowercase=True,
                        strip_accents="unicode",
                        max_features=2500,
                        sublinear_tf=True
                    )
                ),
                (
                    "clf",
                    LogisticRegression(
                        random_state=42,
                        C=1.5,
                        max_iter=500,
                        class_weight="balanced"
                    )
                )
            ])

            self.model.fit(texts, labels)
            self.is_trained = True
            logger.info(f"TicketClassifier trained successfully on {len(texts)} samples.")

        except Exception as e:
            logger.exception(f"Failed to train TicketClassifier: {e}")
            self.is_trained = False

    def predict(self, message: str) -> Dict[str, Any]:
        """
        Predicts category, calculates calibrated confidence, and determines review flag.

        Returns:
            dict containing:
                - predicted_category: str
                - confidence_score: float (0.0 to 1.0)
                - review_recommendation: bool
                - uncertainty_reason: Optional[str]
        """
        # 1. Validation for empty or whitespace-only messages
        if not message or not message.strip():
            return {
                "predicted_category": "General",
                "confidence_score": 0.0,
                "review_recommendation": True,
                "uncertainty_reason": "Message is empty or contains only whitespace characters."
            }

        cleaned_message = message.strip()

        # 2. Check if model is initialized
        if not self.is_trained or self.model is None:
            return {
                "predicted_category": "General",
                "confidence_score": 0.0,
                "review_recommendation": True,
                "uncertainty_reason": "Classifier pipeline is not trained or initialized."
            }

        try:
            # Predict probabilities across categories
            probabilities = self.model.predict_proba([cleaned_message])[0]
            classes = self.model.classes_

            # Sort probabilities descending
            sorted_indices = np.argsort(probabilities)[::-1]
            top_class_idx = sorted_indices[0]
            top_category = str(classes[top_class_idx])
            top_confidence = float(np.round(probabilities[top_class_idx], 4))

            # Calculate margin between top 1 and top 2 predictions
            second_confidence = float(probabilities[sorted_indices[1]]) if len(sorted_indices) > 1 else 0.0
            margin = float(np.round(top_confidence - second_confidence, 4))

            review_recommendation = False
            uncertainty_reason = None

            # Evaluation of uncertainty criteria
            if top_confidence < UNCERTAINTY_CONFIDENCE_THRESHOLD:
                review_recommendation = True
                uncertainty_reason = (
                    f"Low confidence score ({top_confidence:.2f}) below threshold "
                    f"({UNCERTAINTY_CONFIDENCE_THRESHOLD:.2f})."
                )
            elif margin < UNCERTAINTY_MARGIN_THRESHOLD:
                second_category = str(classes[sorted_indices[1]])
                review_recommendation = True
                uncertainty_reason = (
                    f"Ambiguous prediction: margin ({margin:.2f}) between top class "
                    f"'{top_category}' ({top_confidence:.2f}) and runner-up "
                    f"'{second_category}' ({second_confidence:.2f}) is narrow."
                )

            return {
                "predicted_category": top_category,
                "confidence_score": top_confidence,
                "review_recommendation": review_recommendation,
                "uncertainty_reason": uncertainty_reason
            }

        except Exception as e:
            logger.exception(f"Error during prediction: {e}")
            return {
                "predicted_category": "General",
                "confidence_score": 0.0,
                "review_recommendation": True,
                "uncertainty_reason": f"Classification computation failed: {str(e)}"
            }


# Singleton instance for application reuse
_classifier_instance: Optional[TicketClassifier] = None


def get_classifier() -> TicketClassifier:
    """Provides a singleton instance of TicketClassifier."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = TicketClassifier()
    return _classifier_instance
