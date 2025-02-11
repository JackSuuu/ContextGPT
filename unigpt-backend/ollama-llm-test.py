import ollama

response = ollama.chat(model="deepseek-r1:1.5b", messages=[{"role": "user", "content": "What is AI?"}])
print(response["message"]["content"])
