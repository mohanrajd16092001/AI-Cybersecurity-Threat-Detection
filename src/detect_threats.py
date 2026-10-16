import joblib
import matplotlib.pyplot as plt
import pandas as pd

from load_data import FEATURE_COLUMNS, PROJECT_ROOT, load_dataset


def detect_threats():
    model_path = (
        PROJECT_ROOT / "models" / "threat_detection_pipeline.joblib"
    )

    if not model_path.is_file():
        raise FileNotFoundError("Train the model first.")

    model = joblib.load(model_path)

    # Replay a small batch of recorded traffic.
    data = load_dataset("KDDTest.txt").head(200).copy()
    features = data[FEATURE_COLUMNS]

    predictions = model.predict(features)

    # Locate the probability column for class 1: attack.
    attack_index = list(model.classes_).index(1)
    scores = model.predict_proba(features)[:, attack_index]

    results = pd.DataFrame(
        {
            "record_id": data.index,
            "actual_attack_type": data["attack_label"],
            "actual_is_attack": data["is_attack"],
            "predicted_is_attack": predictions,
            "attack_score": scores,
        }
    )

    results["alert"] = results["predicted_is_attack"].map(
        {
            0: "NO ALERT",
            1: "SUSPICIOUS TRAFFIC",
        }
    )

    alerts = results[
        results["predicted_is_attack"] == 1
    ].copy()

    missed = results[
        (results["actual_is_attack"] == 1)
        & (results["predicted_is_attack"] == 0)
    ]

    output_folder = PROJECT_ROOT / "outputs"
    image_folder = PROJECT_ROOT / "images"
    output_folder.mkdir(parents=True, exist_ok=True)
    image_folder.mkdir(parents=True, exist_ok=True)

    results.to_csv(
        output_folder / "simulation_predictions.csv",
        index=False,
    )
    alerts.to_csv(
        output_folder / "threat_alerts.csv",
        index=False,
    )

    # Actual labels help reveal attacks receiving low scores.
    fig, ax = plt.subplots(figsize=(11, 5))

    for label, name, color in [
        (0, "Actual normal", "blue"),
        (1, "Actual attack", "red"),
    ]:
        group = results[results["actual_is_attack"] == label]
        ax.scatter(
            group["record_id"],
            group["attack_score"],
            label=name,
            color=color,
            alpha=0.65,
            s=25,
        )

    ax.axhline(
        0.5,
        color="black",
        linestyle="--",
        label="0.5 score reference",
    )
    ax.set_xlabel("Test record index")
    ax.set_ylabel("Model attack score")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("Dataset Replay: First 200 Test Records")
    ax.legend()
    fig.tight_layout()
    fig.savefig(
        image_folder / "threat_detection_simulation.png",
        dpi=150,
    )
    plt.close(fig)

    print("DATASET REPLAY SIMULATION")
    print(f"Records processed: {len(results)}")
    print(f"Alerts generated: {len(alerts)}")
    print(f"Actual attacks missed: {len(missed)}")
    print("\nFirst 10 alerts:")
    print(alerts.head(10).to_string(index=False))
    print("\nPredictions, alerts, and simulation graph saved.")
    print("Attack scores are model outputs, not verified probabilities.")


if __name__ == "__main__":
    detect_threats()