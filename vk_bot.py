from dotenv import load_dotenv
import os
import random

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow


def get_dialogflow_response(session_id, text, project_id):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code="ru")
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result.fulfillment_text


def send_response(event, api, PROJECT_ID):
    dialogflow_response = get_dialogflow_response(
        session_id=str(event.user_id),
        text=event.text,
        project_id=PROJECT_ID
    )

    api.messages.send(
        user_id=event.user_id,
        message=dialogflow_response,
        random_id=random.randint(1, 1000)
    )


def main():
    load_dotenv()
    VK_BOT_TOKEN = os.environ['VK_TOKEN']
    PROJECT_ID = os.environ['DIALOGFLOW_PROJECT_ID']

    vk_session = vk_api.VkApi(token=VK_BOT_TOKEN)
    api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            send_response(event, api, PROJECT_ID)


if __name__ == '__main__':
    main()
