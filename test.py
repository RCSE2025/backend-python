from app.ollama import create_openai_instance

with open("prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

    instance = create_openai_instance(system_prompt)

    reply = instance("Как зарегистрироваться на платформе?")

    print(reply)

    print()

    reply = instance("Как добавить товар?")

    print(reply)