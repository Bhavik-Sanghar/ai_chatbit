from app.services.chat_service import ChatService


def main():
    chat_service = ChatService()

    chat = chat_service.create_chat()

    print(f"Created chat: {chat.session_id}")

    response = chat_service.chat(
        session_id=chat.session_id,
        question="What is Python?",
    )

    print(response)


if __name__ == "__main__":
    main()
