import json
from pprint import pprint
import os

from google.cloud import dialogflow
from dotenv import load_dotenv


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)

    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=[message_texts])
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    print("Intent created: {}".format(response))


def main():
    load_dotenv()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(script_dir, "questions.json")

    with open(file_name, "r", encoding='utf-8') as file:
        questions = json.load(file)

    PROJECT_ID = os.environ['DIALOGFLOW_PROJECT_ID']

    for intent_name, intent_data in questions.items():
        create_intent(
            project_id=PROJECT_ID,
            display_name=intent_name,
            training_phrases_parts=intent_data['questions'],
            message_texts=intent_data['answer']
        )


if __name__ == '__main__':
    main()
