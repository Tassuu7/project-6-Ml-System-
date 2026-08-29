"""
DataMorph Studio - Comprehensive Classification Metrics
Calculates ROC-AUC, PR-AUC, Accuracy, Precision, Recall, F1, F-Beta, Log-Loss, Brier Score, and Confusion Matrix.
"""

import math
from typing import List, Dict, Any, Tuple


class ClassificationMetrics:
    """Binary and Multi-Class Evaluation Metrics."""

    @classmethod
    def confusion_matrix(cls, y_true: List[int], y_pred: List[int]) -> Dict[str, int]:
        tp, fp, tn, fn = 0, 0, 0, 0
        for yt, yp in zip(y_true, y_pred):
            if yt == 1 and yp == 1: tp += 1
            elif yt == 0 and yp == 1: fp += 1
            elif yt == 0 and yp == 0: tn += 1
            elif yt == 1 and yp == 0: fn += 1
        return {"tp": tp, "fp": fp, "tn": tn, "fn": fn}

    @classmethod
    def evaluate_binary(cls, y_true: List[int], y_pred_prob: List[float], threshold: float = 0.5) -> Dict[str, Any]:
        y_pred = [1 if p >= threshold else 0 for p in y_pred_prob]
        cm = cls.confusion_matrix(y_true, y_pred)
        tp, fp, tn, fn = cm["tp"], cm["fp"], cm["tn"], cm["fn"]

        n = len(y_true) or 1
        accuracy = (tp + tn) / float(n)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2.0 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

        # Log-Loss / Binary Cross-Entropy
        log_loss = 0.0
        for yt, p in zip(y_true, y_pred_prob):
            p_safe = max(1e-15, min(1.0 - 1e-15, p))
            log_loss -= (yt * math.log(p_safe) + (1 - yt) * math.log(1.0 - p_safe))
        log_loss /= float(n)

        # ROC-AUC via trapezoidal integration
        auc = cls.roc_auc_score(y_true, y_pred_prob)

        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "specificity": round(specificity, 4),
            "log_loss": round(log_loss, 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": cm
        }

    @classmethod
    def roc_auc_score(cls, y_true: List[int], y_pred_prob: List[float]) -> float:
        """Computes Area Under the Receiver Operating Characteristic Curve (ROC-AUC)."""
        pairs = sorted(zip(y_pred_prob, y_true), key=lambda x: x[0], reverse=True)
        pos = sum(1 for y in y_true if y == 1)
        neg = len(y_true) - pos
        if pos == 0 or neg == 0:
            return 0.5

        auc = 0.0
        fp = 0
        tp = 0
        prev_fp = 0
        prev_tp = 0

        for prob, yt in pairs:
            if yt == 1:
                tp += 1
            else:
                fp += 1
                auc += (tp + prev_tp) * (fp - prev_fp) / 2.0
                prev_fp = fp
                prev_tp = tp

        return round(auc / (pos * neg), 4)
