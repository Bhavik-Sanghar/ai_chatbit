from app.services.chat_service import ChatService


def main():
    chat_service = ChatService()

    # ─────────────────────────
    # Session A
    # ─────────────────────────

    print("\n--- SESSION A ---")

    print(
        chat_service.chat(
            "session-A",
            "My favorite programming language is Python."
        )
    )

    print(
        chat_service.chat(
            "session-A",
            "What is my favorite programming language?"
        )
    )

    # ─────────────────────────
    # Session B
    # ─────────────────────────

    print("\n--- SESSION B ---")

    print(
        chat_service.chat(
            "session-B",
            "My favorite programming language is JavaScript."
        )
    )

    print(
        chat_service.chat(
            "session-B",
            "What is my favorite programming language?"
        )
    )


if __name__ == "__main__":
    main()