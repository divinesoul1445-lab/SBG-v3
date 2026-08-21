from pathlib import Path
import shutil

from modules.pipeline import Pipeline


def clear_output_folder():

    output_folder = Path(
        "output"
    )

    if output_folder.exists():

        print()
        print("=" * 80)
        print("CLEANING PREVIOUS OUTPUT")
        print("=" * 80)

        print(
            f"Removing: {output_folder.resolve()}"
        )

        shutil.rmtree(
            output_folder
        )

        print(
            "✓ Previous output folder removed."
        )

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"✓ Fresh output folder created: "
        f"{output_folder.resolve()}"
    )

    print()


def main():

    # ==========================================================
    # CLEAN OUTPUT FROM PREVIOUS RUN
    # ==========================================================

    clear_output_folder()

    # ==========================================================
    # RUN PIPELINE
    # ==========================================================

    pipeline = Pipeline()

    pipeline.run()


if __name__ == "__main__":
    main()