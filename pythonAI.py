import openai
import os
import json
from openai import OpenAI

client = OpenAI(
	base_url="https://models.inference.ai.azure.com",
	api_key="(Place GitHub Token Here)"
	)

DB_FILE = "chat_data.json"

def load_history():
	if os.path.exists(DB_FILE):
		with open(DB_FILE, "r") as f:
			return json.load(f)
	return [{"role": "system", "content": "You are a helpful and witty AI assistant."}]

def save_history(history):
	with open(DB_FILE, "w") as f:
		json.dump(history, f, indent=4)

chat_history = load_history()

def chat_with_gpt(prompt):
	chat_history.append({"role": "user", "content": prompt})

	response = client.chat.completions.create(
		model="gpt-4o",
		messages=chat_history
	)

	ai_msg = response.choices[0].message.content.strip()
	chat_history.append({"role": "assistant", "content": ai_msg})

	save_history(chat_history)

	return ai_msg

if __name__ == "__main__":
	print(f"Chatbot loaded memory!")
	while True:
		user_input = input("You: ")
		if user_input.lower() in ["quit", "exit", "bye"]:
			print("Saving and exiting...")
			break

		try:
			bot_text = chat_with_gpt(user_input)
			print("Chatbot: ", bot_text)
		except Exception as e:
			print(f"An error occurred: {e}")
