import math

import joblib
import pandas as pd
from flask import Flask, jsonify, request

from load_data import FEATURE_COLUMNS, PROJECT_ROOT
from preprocess import CATEGORICAL_COLUMNS


MODEL_PATH = (
    PROJECT_ROOT / "models" / "threat_detection_pipeline.joblib"
)

if not MODEL_PATH.is_file():
    raise FileNotFoundError("Train the model before starting the API.")

model = joblib.load(MODEL_PATH)
app = Flask(__name__)


@app.get("/")
def home():
    return jsonify(
        {
            "project": "AI-Powered Cybersecurity Threat Detection",
            "status": "running",
            "prediction_endpoint": "POST /predict",
            "input_format": {"features": "Object with all 41 features"},
            "required_features": FEATURE_COLUMNS,
            "label_mapping": {"0": "Normal", "1": "Attack"},
        }
    )


@app.post("/predict")
def predict():
    if not request.is_json:
        return jsonify(error="Send JSON data."), 415

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify(error="The request must be a JSON object."), 400

    features = payload.get("features")

    if not isinstance(features, dict):
        return jsonify(error="'features' must be a JSON object."), 400

    missing = sorted(set(FEATURE_COLUMNS) - set(features))
    extra = sorted(set(features) - set(FEATURE_COLUMNS))

    if missing or extra:
        return jsonify(
            error="Feature names do not match the training schema.",
            missing_features=missing,
            extra_features=extra,
        ), 400

    cleaned = {}

    for name in FEATURE_COLUMNS:
        value = features[name]

        if name in CATEGORICAL_COLUMNS:
            if not isinstance(value, str) or not value.strip():
                return jsonify(
                    error=f"'{name}' must be a nonempty string."
                ), 400

            cleaned[name] = value.strip()

        else:
            if isinstance(value, bool) or value is None:
                return jsonify(
                    error=f"'{name}' must be a finite number."
                ), 400

            try:
                number = float(value)
            except (TypeError, ValueError, OverflowError):
                return jsonify(
                    error=f"'{name}' must be a finite number."
                ), 400

            if not math.isfinite(number):
                return jsonify(
                    error=f"'{name}' must be a finite number."
                ), 400

            cleaned[name] = number

    # Preserve the same column order and preprocessing as training.
    frame = pd.DataFrame([cleaned], columns=FEATURE_COLUMNS)

    prediction = int(model.predict(frame)[0])
    attack_index = list(model.classes_).index(1)
    attack_score = float(
        model.predict_proba(frame)[0, attack_index]
    )

    return jsonify(
        Threat_Detected=bool(prediction),
        predicted_label="Attack" if prediction == 1 else "Normal",
        attack_score=attack_score,
        alert="SUSPICIOUS TRAFFIC" if prediction == 1 else "NO ALERT",
        score_note="Model score, not a verified probability.",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)