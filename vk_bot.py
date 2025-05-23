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

    if response.query_result.intent.is_fallback:
        return None
    
    return response.query_result.fulfillment_text


def send_response(event, api, PROJECT_ID):
    dialogflow_response = get_dialogflow_response(
        session_id=f"vk_{event.user_id}",
        text=event.text,
        project_id=PROJECT_ID
    )

    if dialogflow_response:
        api.messages.send(
            user_id=event.user_id,
            message=dialogflow_response,
            random_id=random.randint(1, 1000)
        )


def main():
    load_dotenv()
    vk_bot_token = os.environ['VK_TOKEN']
    project_id = os.environ['DIALOGFLOW_PROJECT_ID']

    vk_session = vk_api.VkApi(token=vk_bot_token)
    api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            send_response(event, api, project_id)


if __name__ == '__main__':
    main()
