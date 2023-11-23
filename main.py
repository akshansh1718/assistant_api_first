import os
import time
import logging
from datetime import datetime
import openai

from dotenv import load_dotenv # The dotenv library's load_dotenv function reads a .env file to load environment variables into the process environment. This is a common method to handle configuration settings securely.
# Load env variables
load_dotenv()
# Set up logging
logging.basicConfig(level=logging.INFO)

from openai import OpenAI
client = OpenAI()

filepath = './documents/test.pdf'
file_object = client.files.create(
    file = open(filepath, 'rb'),
    purpose = 'assistants',
)

print(file_object.id)

assistant = client.beta.assistants.create(
    name="Research Assistant",
    instructions="You are a helpful God messenger.You help people in a spiritual way",
    tools=[{"type": "retrieval"}],
    model="gpt-4-1106-preview",
    file_ids=[file_object.id]
)

thread = client.beta.threads.create()


message = "What's this paper about?"

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=message
)

run = client.beta.threads.runs.create(
    thread_id = thread.id,
    assistant_id = assistant.id,
    instructions = "Please address the user queries based upon the document."
)

def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """
    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                logging.info(f"Run completed in {formatted_elapsed_time}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)


wait_for_run_completion(client, thread.id, run.id)

messages = client.beta.threads.messages.list(
    thread_id=thread.id
    )

last_message = messages.data[0]
response = last_message.content[0].text.value
print(response)