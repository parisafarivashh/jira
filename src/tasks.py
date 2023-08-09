from django.db import transaction
from langchain import LLMChain
from langchain.chains import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI
from rest_framework.exceptions import NotFound

from .designPattern.message import MessageFacade
from .models import RoomMember, Room, Message

from .models import Member
from ..jira import celery_app
from ..jira.tasks import MyTask


@celery_app.task(
    base=MyTask,
    autoretry_for=(Exception,),
    name='Create_room_member',
)
@transaction.atomic
def create_room_member(user_id, public_room_id, private_room_id,
                       manager_id=None):
    try:
        private_room = Room.objects.get(id=private_room_id)
        public_room = Room.objects.get(id=public_room_id)

        user = Member.objects.get(id=user_id)
        if manager_id is not None:
            manager = Member.objects.get(id=manager_id)
            RoomMember.objects.bulk_create([
                RoomMember(member_id=manager, room_id=public_room),
                RoomMember(member_id=manager, room_id=private_room),
            ], ignore_conflicts=True)

        RoomMember.objects.bulk_create([
            RoomMember(member_id=user, room_id=public_room),
            RoomMember(member_id=user, room_id=private_room),
        ], ignore_conflicts=True)

    except Exception:
        raise NotFound()


@celery_app.task(
    base=MyTask,
    autoretry_for=(Exception,),
    name='Summary_room',
)
@transaction.atomic
def summary_room(current_user, room_id=None):
    messages = Message.objects.filter(room_id=room_id).all()
    user_bot = Member.objects.get_or_create(
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

        # Define LLM chain
        llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo-16k",
            openai_api_key='openai_api.key',
        )
        llm_chain = LLMChain(llm=llm, prompt=prompt)

        # Define StuffDocumentsChain
        stuff_chain = StuffDocumentsChain(
            llm_chain=llm_chain, document_variable_name="text"
        )

        docs = messages
        summary_message = stuff_chain.run(docs)
        print(summary_message)

        room = Room.get_room_object(room_id)
        RoomMember.objects.get_or_create(
            room_id=room.id,
            member_id=user_bot.id
        )
        message = Message(
            type='message',
            sender_id=user_bot.id,
            body=summary_message,
            room_id=room_id,
        )

        MessageFacade(
            message=message,
            room=Room,
            user=current_user
        ).send_message()

