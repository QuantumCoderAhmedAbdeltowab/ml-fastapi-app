# import subprocess
# from typing import List
# from models import Message, Role

# # 1) system prompt lives here
# SYSTEM_PROMPT = (
#     "You are a cybersecurity assistant. You answer questions related to cybersecurity,"
#     "online safety, and best practices for digital security."
#     "Try to answer as briefly as possible."
# )

# def build_prompt(history: List[Message], new_q_en: str) -> str:
#     """
#     Turn the list of prior Message objects + the new (English) question
#     into one big string for the model.
#     """
#     parts = []
#     for msg in history:
#         if not msg.role or not msg.content:
#             raise ValueError("Invalid message in history: missing role or content.")
#         # roles are Enum('user','assistant')
#         parts.append(f"{msg.role.value.capitalize()}: {msg.content}")
#     parts.append(f"User: {new_q_en}")
#     return SYSTEM_PROMPT + "\n\n" + "\n".join(parts) + "\nAssistant:"

# def query_ollama(prompt: str) -> str:
#     """
#     Actually call the Ollama CLI with the fully assembled prompt.
#     """
#     command = ["ollama", "run", "llama3.2:1b"]
#     process = subprocess.run(
#         command,
#         input=prompt,
#         text=True,
#         capture_output=True
#     )
#     if process.returncode != 0:
#         raise Exception(f"Ollama failed: {process.stderr}")
#     return process.stdout.strip()

# def chat_with_ollama(history: List[Message], new_q_en: str) -> str:
#     """
#     Convenience: assemble + call
#     """
#     prompt = build_prompt(history, new_q_en)
#     return query_ollama(prompt)

