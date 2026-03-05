import ollama
response = ollama.chat(model='gemma2:2b', messages=[{'role': 'user', 'content': 'Dis bonjour en français en une phrase'}])
print(response['message']['content'])