import json
from pathlib import Path

from src.ingestion.fda_label_loader import load_fda_labels
from src.preprocessing.chunker import make_fda_label_chunks


# ==========================================================
# PROJECT PATHS
# ==========================================================

# Current file:
# trialgaurd-ai-ml/scripts/build_fda_kb.py
#
# parents[1] ->
# trialgaurd-ai-ml/

PROJECT_ROOT = Path(__file__).resolve().parents[1]


FDA_LABEL_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "fda_labels"
)


OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "fda_label_chunks.jsonl"
)


# ==========================================================
# FIND FDA FILES
# ==========================================================

def find_fda_files() -> list[Path]:
    """
    Find all supported FDA Drug Label files.

    Supported:
        *.json
        *.zip

    Returns sorted list of Paths.
    """

    json_files = list(
        FDA_LABEL_DIR.glob("*.json")
    )

    zip_files = list(
        FDA_LABEL_DIR.glob("*.zip")
    )

    files = json_files + zip_files

    return sorted(
        files,
        key=lambda path: path.name.lower()
    )


# ==========================================================
# PROCESS ONE FDA FILE
# ==========================================================

def process_fda_file(
    path: Path,
    output
) -> tuple[int, int]:
    """
    Process one FDA Drug Label dataset file.

    Returns:
        (number_of_labels, number_of_chunks)
    """

    label_count = 0
    chunk_count = 0

    for label in load_fda_labels(path):

        label_count += 1

        chunks = make_fda_label_chunks(
            label
        )

        for chunk in chunks:

            output.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False
                )
                + "\n"
            )

            chunk_count += 1

    return (
        label_count,
        chunk_count
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 70)
    print(
        "TrialGuard AI - Building FDA Drug Label Knowledge Base"
    )
    print("=" * 70)

    print(
        f"\nProject root:\n{PROJECT_ROOT}"
    )

    print(
        f"\nFDA label directory:\n{FDA_LABEL_DIR}"
    )

    print(
        f"\nOutput file:\n{OUTPUT_FILE}"
    )

    # ------------------------------------------------------
    # Check raw FDA label directory
    # ------------------------------------------------------

    if not FDA_LABEL_DIR.exists():

        raise FileNotFoundError(
            "\nFDA label directory does not exist:\n"
            f"{FDA_LABEL_DIR}"
        )

    # ------------------------------------------------------
    # Find all .json and .zip files
    # ------------------------------------------------------

    files = find_fda_files()

    print("\n" + "-" * 70)

    print(
        f"FDA label files discovered: {len(files)}"
    )

    if not files:

        raise FileNotFoundError(
            "\nNo FDA label dataset files were found.\n\n"
            "Expected .json or .zip files inside:\n"
            f"{FDA_LABEL_DIR}"
        )

    # ------------------------------------------------------
    # Display discovered files
    # ------------------------------------------------------

    print("\nFiles that will be processed:")

    for index, path in enumerate(
        files,
        start=1
    ):

        size_mb = (
            path.stat().st_size
            / (1024 * 1024)
        )

        print(
            f"  {index:02d}. "
            f"{path.name} "
            f"({size_mb:.2f} MB)"
        )

    # ------------------------------------------------------
    # Create output directory
    # ------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ------------------------------------------------------
    # Counters
    # ------------------------------------------------------

    total_labels = 0
    total_chunks = 0

    successful_files = 0
    failed_files = []

    # ------------------------------------------------------
    # IMPORTANT:
    #
    # "w" intentionally rebuilds the FDA chunk file.
    #
    # Existing fda_label_chunks.jsonl will be replaced.
    # ------------------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as output:

        # --------------------------------------------------
        # Process each FDA file separately
        # --------------------------------------------------

        for file_index, path in enumerate(
            files,
            start=1
        ):

            print("\n" + "=" * 70)

            print(
                f"[{file_index}/{len(files)}] "
                f"Processing:"
            )

            print(
                path.name
            )

            print("-" * 70)

            try:

                (
                    labels_in_file,
                    chunks_in_file
                ) = process_fda_file(
                    path,
                    output
                )

                total_labels += (
                    labels_in_file
                )

                total_chunks += (
                    chunks_in_file
                )

                successful_files += 1

                print(
                    f"Labels in file : "
                    f"{labels_in_file}"
                )

                print(
                    f"Chunks in file : "
                    f"{chunks_in_file}"
                )

                print(
                    f"Total labels   : "
                    f"{total_labels}"
                )

                print(
                    f"Total chunks   : "
                    f"{total_chunks}"
                )

            except Exception as error:

                # Do not destroy progress from previous files.
                # Record this file and continue.

                print(
                    "\nERROR while processing:"
                )

                print(
                    path.name
                )

                print(
                    f"Error type: "
                    f"{type(error).__name__}"
                )

                print(
                    f"Error: {error}"
                )

                failed_files.append({
                    "file":
                        path.name,

                    "error":
                        str(error)
                })

    # ======================================================
    # FINAL SUMMARY
    # ======================================================

    print("\n" + "=" * 70)

    print(
        "FDA DRUG LABEL KNOWLEDGE BASE BUILD COMPLETE"
    )

    print("=" * 70)

    print(
        f"\nFiles discovered : "
        f"{len(files)}"
    )

    print(
        f"Files successful : "
        f"{successful_files}"
    )

    print(
        f"Files failed     : "
        f"{len(failed_files)}"
    )

    print(
        f"Labels processed : "
        f"{total_labels}"
    )

    print(
        f"Chunks generated : "
        f"{total_chunks}"
    )

    # ------------------------------------------------------
    # Output file information
    # ------------------------------------------------------

    if OUTPUT_FILE.exists():

        output_size_mb = (
            OUTPUT_FILE.stat().st_size
            / (1024 * 1024)
        )

        print(
            f"\nOutput size      : "
            f"{output_size_mb:.2f} MB"
        )

    print(
        f"\nOutput file:\n"
        f"{OUTPUT_FILE}"
    )

    # ------------------------------------------------------
    # Failed files
    # ------------------------------------------------------

    if failed_files:

        print("\n" + "-" * 70)

        print(
            "FILES THAT FAILED:"
        )

        for item in failed_files:

            print(
                f"\nFile: "
                f"{item['file']}"
            )

            print(
                f"Reason: "
                f"{item['error']}"
            )

        print(
            "\nThe other successfully processed "
            "files are still present in the output."
        )

    else:

        print(
            "\nAll FDA label files were "
            "processed successfully."
        )

    print("\n" + "=" * 70)


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()