# import subprocess

# def query_ollama(prompt: str) -> str:
#     """
#     Prepares the prompt by adding a system message that instructs the model
#     to act as a cybersecurity assistant. Then, it calls the Ollama command-line tool
#     to run the Llama 3.2 model.
#     """
#     system_prompt = (
#         "You are a cybersecurity assistant. You answer questions related to cybersecurity, "
#         "online safety, and best practices for digital security. If a question is not related "
#         "to these domains, politely let the user know that you cannot provide assistance on that topic."
#         # "when answering a question that is written in arabic, translate it to english before answering it, and then translate the answer back to arabic."
#         "try to answer the question as short as posible."
#     )
#     # Combine the system instruction with the user question.
#     final_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"

#     # Command to run the model via Ollama
#     command = ["ollama", "run", "llama3.2"]

#     # Run the command with the prompt passed to the process’ standard input.
#     process = subprocess.run(command, input=final_prompt, text=True, capture_output=True)
    
#     if process.returncode != 0:
#         raise Exception(f"Ollama command failed: {process.stderr}")
    
#     return process.stdout.strip()
import subprocess

def query_ollama(prompt: str) -> str:
    """
    Prepares the prompt by adding a system message that instructs the model
    to act as a cybersecurity assistant. Then, it calls the Ollama command-line tool
    to run the Llama 3.2 model.
    """
    system_prompt = (
        "You are a cybersecurity assistant. You answer questions related to cybersecurity, "
        "online safety, and best practices for digital security. If a question is not related "
        "to these domains, politely let the user know that you cannot provide assistance on that topic."
        "try to answer the question as short as posible."
    )
    # Combine the system instruction with the user's prompt.
    final_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"

    # Command to run the model via Ollama
    command = ["ollama", "run", "llama3.2:1b"]

    # Run the command with the prompt passed via standard input.
    process = subprocess.run(command, input=final_prompt, text=True, capture_output=True)
    
    if process.returncode != 0:
        raise Exception(f"Ollama command failed: {process.stderr}")
    
    return process.stdout.strip()

