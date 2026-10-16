import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from load_data import FEATURE_COLUMNS, PROJECT_ROOT, load_dataset
from preprocess import build_preprocessor


def train_model():
    print("Loading training data...")
    data = load_dataset("KDDTrain.txt")

    # Only network features go into the model.
    # Attack labels and difficulty are excluded.
    X_train = data[FEATURE_COLUMNS]
    y_train = data["is_attack"]

    print(f"Training records: {len(X_train):,}")
    print(f"Input features: {len(FEATURE_COLUMNS)}")
    print("Target: 0 = normal, 1 = attack")

    # Save preprocessing and the classifier together.
    # Predictions will use the same transformations as training.
    pipeline = Pipeline(
        steps=[
            ("preprocessing", build_preprocessor()),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=100,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    print("Training Random Forest. Please wait...")
    pipeline.fit(X_train, y_train)

    model_folder = PROJECT_ROOT / "models"
    model_folder.mkdir(parents=True, exist_ok=True)

    model_path = model_folder / "threat_detection_pipeline.joblib"
    joblib.dump(pipeline, model_path)

    print("\nTraining completed.")
    print(f"Model saved to: {model_path}")
    print("The testing dataset has not been used during training.")


if __name__ == "__main__":
    train_model()