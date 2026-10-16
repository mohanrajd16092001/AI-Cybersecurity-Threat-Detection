from pathlib import Path
import pandas as pd

# Find the project folder, regardless of where the command is run.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# The dataset has no header row, so we supply column names.
FEATURE_COLUMNS = [
    "duration", "protocol_type", "service", "flag",
    "src_bytes", "dst_bytes", "land", "wrong_fragment",
    "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted",
    "num_root", "num_file_creations", "num_shells",
    "num_access_files", "num_outbound_cmds",
    "is_host_login", "is_guest_login", "count", "srv_count",
    "serror_rate", "srv_serror_rate", "rerror_rate",
    "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
    "srv_diff_host_rate", "dst_host_count",
    "dst_host_srv_count", "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
    "dst_host_srv_serror_rate", "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
]

ALL_COLUMNS = FEATURE_COLUMNS + ["attack_label", "difficulty"]


def load_dataset(filename):
    """Read a dataset and check its basic structure."""
    file_path = PROJECT_ROOT / "data" / filename

    if not file_path.is_file():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    data = pd.read_csv(file_path, header=None)

    if data.empty:
        raise ValueError(f"{filename} is empty.")

    if data.shape[1] != len(ALL_COLUMNS):
        raise ValueError(
            f"{filename}: expected 43 columns, "
            f"but found {data.shape[1]}."
        )

    data.columns = ALL_COLUMNS

    if data["attack_label"].isna().any():
        raise ValueError(f"{filename} contains missing attack labels.")

    # Keep the original attack names and add a binary target.
    data["attack_label"] = (
        data["attack_label"].astype(str).str.strip().str.lower()
    )

    if data["attack_label"].eq("").any():
        raise ValueError(f"{filename} contains empty attack labels.")

    # 0 means normal traffic; 1 means an attack.
    data["is_attack"] = (
        data["attack_label"] != "normal"
    ).astype(int)

    return data


if __name__ == "__main__":
    for filename in ["KDDTrain.txt", "KDDTest.txt"]:
        dataset = load_dataset(filename)

        print(f"\nFile: {filename}")
        print(f"Records: {len(dataset):,}")
        print(f"Input features: {len(FEATURE_COLUMNS)}")
        print(f"Normal records: {(dataset['is_attack'] == 0).sum():,}")
        print(f"Attack records: {(dataset['is_attack'] == 1).sum():,}")
        print(f"Missing values: {dataset.isna().sum().sum():,}")
        print("Attack labels:")
        print(dataset["attack_label"].value_counts().to_string())