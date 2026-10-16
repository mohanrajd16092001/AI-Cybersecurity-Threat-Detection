import json

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    precision_recall_fscore_support,
)

from load_data import FEATURE_COLUMNS, PROJECT_ROOT, load_dataset


def evaluate_model():
    model_path = (
        PROJECT_ROOT / "models" / "threat_detection_pipeline.joblib"
    )

    if not model_path.is_file():
        raise FileNotFoundError("Train the model before evaluating it.")

    print("Loading the saved model and testing data...")
    model = joblib.load(model_path)
    data = load_dataset("KDDTest.txt")

    X_test = data[FEATURE_COLUMNS]
    y_test = data["is_attack"]

    print(f"Evaluating {len(data):,} testing records...")
    predictions = model.predict(X_test)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test,
        predictions,
        average="binary",
        pos_label=1,
        zero_division=0,
    )

    metrics = {
        "test_records": len(data),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "attack_precision": float(precision),
        "attack_recall": float(recall),
        "attack_f1": float(f1),
    }

    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["Normal", "Attack"],
        zero_division=0,
        digits=4,
    )

    output_folder = PROJECT_ROOT / "outputs"
    image_folder = PROJECT_ROOT / "images"
    output_folder.mkdir(parents=True, exist_ok=True)
    image_folder.mkdir(parents=True, exist_ok=True)

    # Save measured results for documentation.
    (output_folder / "metrics.json").write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    (output_folder / "classification_report.txt").write_text(
        report,
        encoding="utf-8",
    )

    results = pd.DataFrame(
        {
            "record_id": range(len(data)),
            "actual_attack_type": data["attack_label"],
            "actual_is_attack": y_test,
            "predicted_is_attack": predictions,
        }
    )
    results.to_csv(
        output_folder / "test_predictions.csv",
        index=False,
    )

    # Rows show actual labels; columns show predicted labels.
    fig, ax = plt.subplots(figsize=(7, 6))
    ConfusionMatrixDisplay.from_predictions(
        y_test,
        predictions,
        labels=[0, 1],
        display_labels=["Normal", "Attack"],
        cmap="Blues",
        colorbar=False,
        ax=ax,
    )
    ax.set_title("NSL-KDD Test Set Confusion Matrix")
    fig.tight_layout()
    fig.savefig(
        image_folder / "confusion_matrix.png",
        dpi=150,
    )
    plt.close(fig)

    print("\nEvaluation results:")
    for name, value in metrics.items():
        if name != "test_records":
            print(f"{name}: {value:.4f}")

    print("\nClassification report:")
    print(report)
    print(f"Results saved to: {output_folder}")
    print(f"Confusion matrix saved to: {image_folder}")


if __name__ == "__main__":
    evaluate_model()