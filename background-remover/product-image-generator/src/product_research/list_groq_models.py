import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


def main():

    api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not api_key:

        print(
            "ERROR: GROQ_API_KEY was not found."
        )

        return


    print("GROQ_API_KEY found.")
    print("Fetching available models...")


    try:

        client = Groq(
            api_key=api_key
        )

        models = client.models.list()


        print("\n" + "=" * 60)
        print("AVAILABLE GROQ MODELS")
        print("=" * 60)


        for model in models.data:

            print(
                f"\nModel: {model.id}"
            )


    except Exception as error:

        print("\nFAILED!")

        print(
            type(error).__name__
        )

        print(error)


if __name__ == "__main__":
    main()