from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from load_data import FEATURE_COLUMNS


# These columns contain categories rather than measurements.
CATEGORICAL_COLUMNS = [
    "protocol_type",
    "service",
    "flag",
]

NUMERIC_COLUMNS = [
    column
    for column in FEATURE_COLUMNS
    if column not in CATEGORICAL_COLUMNS
]


def build_preprocessor():
    """Create preprocessing steps without fitting them yet."""

    # Fill missing numeric values and scale the measurements.
    numeric_pipeline = Pipeline(
        steps=[
            ("fill_missing", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )

    # Fill missing categories and convert categories into numbers.
    categorical_pipeline = Pipeline(
        steps=[
            (
                "fill_missing",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "encode",
                OneHotEncoder(handle_unknown="ignore"),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_COLUMNS),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_COLUMNS,
            ),
        ],
        remainder="drop",
    )