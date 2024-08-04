# jira


- toDo list

   
- 
   - models:
     - [x] member --> used BaseUserManager 
     - [x] project  
     - [x] room
     - [x] room-member
     - [x] message
     - [x] messageMemberSeen
     - [x] task
     - [x] assignment
     - [x] GenericForeignKey 
     - [x] custom signal

- [x] -----------------------------------------------------------------------------------------

  - [x] login/sign in --> with jwt
  - [x] models inherits from basemodel --> baseModel is abstract model that has two filed
  - [x] models inherits from soft_delete --> soft delete is abstract model that has removed_at filed
  - [x] if project created --> privateRoom, publicRoom created for project --> message "created" sent to public room
  - [x] The user could seen message --> if member is a member of room then latest-seen-message updated
  - [x] Send message --> when sending a message to the room... previous messages are seen. 

- [x] -----------------------------------------------------------------------------------------

  - [x] Used extra action of ViewSets (Added Custom endpoint to seen message and edit message)
  - [x] bulky-create with ignore_conflicts
  - [x] custom pagination and LimitOffsetPagination
  - [x] django_filters used to get a list of unread messages
  - [x] list members who have seen the message 
   
- [x] ------------------------------------------------------------------------------------
   
  - [x] create/list/update tasks
  - [x] create/list/update assignment

 
 - [x] Implemented celery-task    
 - [x] Used Signals post-save for updating status of the assignment
 - [x] API to get a summary of the room and send it as a message -> Used AI (LANGCHAIN)

- [x] --------------------------------------------------------------------------------------------
 
 - [x] Used swagger for documentation
 - [x] Used django-debug-toolbar
 - [X] Used admin custom(  
         *) Customize Admin Site with ModelAdmin Class  
         *) Use list_select_related           
         *) List Display Custom Fields   
         *) Search field and filter field   
      )
 
 - [x] use SeparateDatabaseAndState in migration django 
 ``` 

class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('src', '0003_rename_private_room_id_task_private_room'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddIndex(
                    model_name='roommember',
                    index=models.Index(fields=['member'], name='room_member_index')
                )
            ],
            database_operations=[
                migrations.RunSQL(
                    """
                    CREATE INDEX "room_member_index" ON "room_member" ("member_id");
                    """,
                    reverse_sql=migrations.RunSQL.noop
                )
            ]
        )

    ]
 ```