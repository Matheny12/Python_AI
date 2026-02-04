import os
import json
import time
from google import genai
from google.genai import types

client = genai.Client(api_key="(Place Gemini Api Key Here)")

DB_FILE = "chat_data.json"
model_ID = "gemini-2.5-flash-lite"

def load_history():
	if os.path.exists(DB_FILE):
		with open(DB_FILE, "r") as f:
			try:
				data = json.load(f)
				formatted_history = []
				for entry in data:
					if entry["role"] == "system": continue
					role = "user" if entry["role"] == "user" else "model"
					formatted_history.append({
						"role": role,
						"parts": [{"text": entry["content"]}]
					})
				return formatted_history
			except (json.JSONDecodeError, KeyError):
				return []
	return []

def save_history(gemini_history):
	serializable_history = []
	for message in gemini_history:
		role = "user" if message.role == "user" else "assistant"
		content = message.parts[0].text
		serializable_history.append({"role": role, "content": content})
	with open(DB_FILE, "w") as f:
		json.dump(serializable_history, f, indent=4)

initial_history = load_history()

chat_session = client.chats.create(
	model=model_ID,
	config=types.GenerateContentConfig(
		system_instruction="You are a helpful and witty AI assistant."
	),
	history=initial_history
)


def chat_with_gemini(prompt):
	max_retries = 3
	retry_delay = 2
	
	for attempt in range(max_retries):
		try:

			response = chat_session.send_message(prompt)

			save_history(chat_session._curated_history)

			return response.text
	
		except Exception as e:
			if "503" in str(e) or "429" in str(e):
				if attempt < max_retries - 1:
					print(f"Server Busy, Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
					time.sleep(retry_delay)
					retry_delay *= 2
				else:
					return "AI too busy, please try again."
			else:
				raise e
	
if __name__ == "__main__":
	print(f"Chatbot loaded memory!")
	while True:
		user_input = input("You: ")
		print("")

		if user_input.lower() in ["quit", "exit", "bye"]:
			print("Saving and exiting...")
			break

		try:
			bot_text = chat_with_gemini(user_input)
			print("Chatbot: ", bot_text)
			print("")
		except Exception as e:
			print(f"An error occurred: {e}")
