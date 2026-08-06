"""
SBG V3

Main Entry Point
"""

import traceback

from modules.pipeline import Pipeline


def main():

    print("=" * 70)
    print("Shree Bhagavad Gita AI Video Generator (V3)")
    print("=" * 70)
    print()

    pipeline = Pipeline()

    try:

        pipeline.run()

        print()
        print("=" * 70)
        print("Video Generated Successfully")
        print("=" * 70)

    except KeyboardInterrupt:

        print()
        print("Generation cancelled by user.")

    except Exception as e:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)

        print(e)

        print()

        traceback.print_exc()


if __name__ == "__main__":

    main()