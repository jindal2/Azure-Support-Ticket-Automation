"""
Test Machine Learning Classifier & Dataset Integrity
"""

import json
from pathlib import Path
from app.classifier import get_classifier, TicketClassifier, SUPPORTED_CATEGORIES
from scripts.evaluate_model import run_evaluation


def test_classifier_initialization():
    """Validates classifier pipeline loads and fits training data successfully."""
    classifier = get_classifier()
    assert classifier.is_trained is True
    assert classifier.model is not None


def test_valid_classification_output_structure():
    """Verifies predict returns expected schema with category, score, and recommendation."""
    classifier = get_classifier()
    result = classifier.predict("I was charged twice on my monthly credit card bill.")
    assert result["predicted_category"] in SUPPORTED_CATEGORIES
    assert isinstance(result["confidence_score"], float)
    assert 0.0 <= result["confidence_score"] <= 1.0
    assert isinstance(result["review_recommendation"], bool)


def test_empty_message_handling():
    """Verifies that empty strings are safely handled and flagged for human review."""
    classifier = get_classifier()
    res1 = classifier.predict("")
    assert res1["review_recommendation"] is True
    assert "whitespace" in res1["uncertainty_reason"].lower() or "empty" in res1["uncertainty_reason"].lower()

    res2 = classifier.predict("   \n\t   ")
    assert res2["review_recommendation"] is True


def test_held_out_dataset_strict_separation():
    """
    Verifies that the held-out test dataset is strictly separate from the training dataset.
    No sample IDs or identical raw texts should overlap.
    """
    backend_dir = Path(__file__).resolve().parent.parent
    train_path = backend_dir / "sample_data" / "train.json"
    test_path = backend_dir / "sample_data" / "test.json"

    with open(train_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)

    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    assert len(train_data) >= 30, "Training set must contain at least 30 samples"
    assert len(test_data) >= 10, "Held-out test set must contain at least 10 samples"

    train_ids = {item["id"] for item in train_data}
    test_ids = {item["id"] for item in test_data}
    train_texts = {item["message"].strip().lower() for item in train_data}
    test_texts = {item["message"].strip().lower() for item in test_data}

    # Strict separation assertions
    assert train_ids.isdisjoint(test_ids), "Test IDs must not overlap with Training IDs"
    assert train_texts.isdisjoint(test_texts), "Test text must not overlap with Training text"


def test_model_evaluation_runs_and_reports_held_out_metrics():
    """Verifies that the evaluate_model script executes against held-out data and returns valid metrics."""
    metrics = run_evaluation()
    assert "accuracy" in metrics
    assert "macro_f1" in metrics
    assert metrics["n_train"] >= 30
    assert metrics["n_test"] >= 10
    assert 0.0 <= metrics["accuracy"] <= 1.0
