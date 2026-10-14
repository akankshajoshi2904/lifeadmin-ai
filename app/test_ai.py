
"""Manual test for the OpenAI API client.

Run this file only when API credits are available.
"""

from app.ai_client import ask_ai


def main():
    answer = ask_ai(
        "Say hello to LifeAdmin AI in one short sentence."
    )
    print(answer)


if __name__ == "__main__":
    main()
