from openai import OpenAI

client = OpenAI(base_url="http://31.128.49.187:11434/v1", api_key="ollama")

def create_openai_instance(system_prompt: str):
    chat_history = []
    def chat_with_openai(user_message: str):
        messages = [{"role": "system", "content": system_prompt}] + chat_history
        messages.append({"role": "user", "content": user_message})
        
        response = client.beta.chat.completions.parse(
            model="llama3.2",
            messages=messages,
            temperature=0.3
        )
        
        reply = response.choices[0].message.content
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": reply})
        
        return reply
    
    return chat_with_openai
