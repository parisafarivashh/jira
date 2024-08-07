import environ
from celery import shared_task
from django.contrib.auth import get_user_model

from django.db import transaction
from django.apps import apps
from langchain import schema, chat_models
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404

from .designPattern.message import MessageFacade
from .models import RoomMember, Room, Message

from jira.tasks import MyTask


env = environ.Env()
environ.Env.read_env()
Member = get_user_model()


@shared_task(
    base=MyTask,
    autoretry_for=(Exception,),
    name='Create_room_member',
)
@transaction.atomic
def create_room_member(
        user_id: int,
        public_room_id: int,
        private_room_id: int,
        manager_id: int = None,
):
    try:
        private_room = Room.objects.get(id=private_room_id)
        public_room = Room.objects.get(id=public_room_id)

        user = Member.objects.get(id=user_id)
        if manager_id is not None:
            manager = Member.objects.get(id=manager_id)
            RoomMember.objects.bulk_create([
                RoomMember(member=manager, room=public_room),
                RoomMember(member=manager, room=private_room),
            ], ignore_conflicts=True)

        RoomMember.objects.bulk_create([
            RoomMember(member=user, room=public_room),
            RoomMember(member=user, room=private_room),
        ], ignore_conflicts=True)

    except Exception:
        raise NotFound()


@shared_task(
    base=MyTask,
    name='Summary_room',
)
@transaction.atomic
def summary_room(current_user_id, room_id=None):
    messages = Message.objects.filter(room_id=room_id) \
        .values_list('body', flat=True)

    summary_message = 'No messages for summary'
    user_bot, created = Member.objects.get_or_create(
        title='bot',
        first_name='bot',
        email='bot@gmail.com',
        password='botPassword',
        role='member',
    )
    if messages.count() != 0:
        prompt = \
            f"""
              Conversation: {messages} \n
              Task: Summarize the entire conversation based on the conversation
              provided above. Your summary should be clear, comprehensive, 
              and contain the essential information from conversation.
            """

        chat = chat_models.ChatOpenAI(
            openai_api_key=env("API_KEY_AI"),
            temperature=0,
            model='gpt-3.5-turbo-16k',
        )
        openai_messages = [
            schema.SystemMessage(
                content='You are a helpful assistant.',
            ),
            schema.HumanMessage(content=prompt),
        ]
        openai_result = chat(openai_messages)
        summary_message = openai_result.content

    room = get_object_or_404(Room, room_id)
    RoomMember.objects.get_or_create(
        room=room,
        member=user_bot
    )
    message = Message(
        type='message',
        sender=user_bot,
        body=summary_message,
        room=room,
    )
    message.save()
    user = Member.objects.get(id=current_user_id)

    MessageFacade(
        message=message,
        room=room,
        user=user
    ).send_message()

