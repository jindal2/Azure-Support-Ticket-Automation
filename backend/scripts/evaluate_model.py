"""
Support Ticket Automation System
Held-Out Model Evaluation Script

Evaluates the scikit-learn classifier pipeline on the held-out test dataset (test.json).
Computes Accuracy, Precision, Recall, F1-Score, Per-Category Metrics, and Confusion Matrix.

Usage:
    python backend/scripts/evaluate_model.py
"""

import json
import os
import sys
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

# Ensure backend package can be imported
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

from app.classifier import TicketClassifier, SUPPORTED_CATEGORIES


def run_evaluation():
    train_path = backend_dir / "sample_data" / "train.json"
    test_path = backend_dir / "sample_data" / "test.json"

    print("======================================================================")
    print("SUPPORT TICKET AUTOMATION — HELD-OUT CLASSIFIER EVALUATION REPORT")
    print("======================================================================\n")

    if not train_path.exists() or not test_path.exists():
        print(f"Error: Dataset files missing.\nTrain: {train_path}\nTest: {test_path}")
        sys.exit(1)

    with open(train_path, "r", encoding="utf-8") as f:
        train_records = json.load(f)

    with open(test_path, "r", encoding="utf-8") as f:
        test_records = json.load(f)

    n_train = len(train_records)
    n_test = len(test_records)

    print(f"Dataset Summary:")
    print(f"  • Training Samples  : {n_train} (across {len(SUPPORTED_CATEGORIES)} categories)")
    print(f"  • Held-Out Test Data: {n_test} (strictly separated from training)")
    print(f"  • Evaluation Strategy: Out-of-Sample generalization test\n")

    # Initialize and train classifier
    classifier = TicketClassifier(data_path=str(train_path))

    if not classifier.is_trained:
        print("Error: Classifier failed to train.")
        sys.exit(1)

    # Evaluate on held-out test set
    y_true = []
    y_pred = []
    confidence_scores = []
    uncertain_count = 0

    print("-" * 70)
    print(f"{'Sample ID':<10} | {'True Category':<12} | {'Predicted':<12} | {'Conf':<6} | {'Status'}")
    print("-" * 70)

    for item in test_records:
        true_cat = item["category"]
        msg = item["message"]
        res = classifier.predict(msg)
        pred_cat = res["predicted_category"]
        conf = res["confidence_score"]
        is_uncertain = res["review_recommendation"]

        y_true.append(true_cat)
        y_pred.append(pred_cat)
        confidence_scores.append(conf)

        if is_uncertain:
            uncertain_count += 1
            status_tag = f"REVIEW ({res.get('uncertainty_reason', '')[:25]}...)"
        else:
            status_tag = "CONFIDENT"

        match_mark = "OK" if true_cat == pred_cat else "MISMATCH"
        print(f"{item['id']:<10} | {true_cat:<12} | {pred_cat:<12} | {conf:<6.2f} | {match_mark} [{status_tag}]")

    print("-" * 70)

    # Calculate overall metrics
    acc = accuracy_score(y_true, y_pred)
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)

    print("\nOVERALL EVALUATION METRICS:")
    print(f"  • Overall Accuracy : {acc * 100:.2f}% ({sum(1 for t, p in zip(y_true, y_pred) if t == p)} / {n_test})")
    print(f"  • Macro Precision  : {macro_p:.4f}")
    print(f"  • Macro Recall     : {macro_r:.4f}")
    print(f"  • Macro F1-Score   : {macro_f1:.4f}")
    print(f"  • Weighted F1-Score: {weighted_f1:.4f}")
    print(f"  • Mean Confidence  : {sum(confidence_scores) / len(confidence_scores):.4f}")
    print(f"  • Flagged for Review: {uncertain_count} / {n_test}")

    print("\nPER-CATEGORY PERFORMANCE BREAKDOWN:")
    report = classification_report(y_true, y_pred, target_names=SUPPORTED_CATEGORIES, labels=SUPPORTED_CATEGORIES, zero_division=0)
    print(report)

    print("CONFUSION MATRIX (Rows: True, Columns: Predicted):")
    labels = SUPPORTED_CATEGORIES
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    row_label = "True \\ Pred"
    header = f"{row_label:<14} | " + " | ".join(f"{lbl:<10}" for lbl in labels)
    print(header)
    print("-" * len(header))
    for i, row in enumerate(cm):
        row_str = f"{labels[i]:<14} | " + " | ".join(f"{val:<10}" for val in row)
        print(row_str)

    print("\n" + "=" * 70)
    print("METHODOLOGY & LIMITATIONS STATEMENT:")
    print("  1. Small Synthetic Baseline: This prototype uses 36 training tickets and 16")
    print("     held-out test tickets to validate end-to-end pipeline functionality.")
    print("  2. In production, real customer data distribution varies by volume and phrasing.")
    print("  3. High model confidence is a statistical probability and not guaranteed truth.")
    print("  4. The system enforces human-in-the-loop review for low confidence and")
    print("     critical/sensitive requests before responses can be finalized.")
    print("======================================================================\n")

    return {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "n_train": n_train,
        "n_test": n_test
    }


if __name__ == "__main__":
    run_evaluation()
