import json
import zipfile
from pathlib import Path


def load_json_file(path: str | Path) -> dict:

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"File does not exist: {path}"
        )

    # Normal JSON
    if path.suffix.lower() == ".json":

        with path.open(
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    # ZIP archive
    if path.suffix.lower() == ".zip":

        with zipfile.ZipFile(
            path,
            "r"
        ) as archive:

            json_files = [
                name
                for name in archive.namelist()
                if name.lower().endswith(".json")
            ]

            if not json_files:

                raise ValueError(
                    f"No JSON file found inside {path}"
                )

            with archive.open(
                json_files[0]
            ) as f:

                return json.loads(
                    f.read().decode("utf-8")
                )

    raise ValueError(
        f"Unsupported file type: {path.suffix}"
    )