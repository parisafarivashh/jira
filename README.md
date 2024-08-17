# jira


- toDo list

   
- 
   - [x] models:
     -  used CustomManager, CustomQueryset , GenericForeignKey, abstract model

-  -----------------------------------------------------------------------------------------

  - [x] login/sign in --> with jwt
  - [x] used nested serializer, to_representation, PrimaryKeyRelatedField, StringRelatedField

-  ----------------------------------------------------------------------------------------


  - [x] Used extra action of ViewSets (Added Custom endpoint)
  - [x] Used Custom filterset class for filtering
  - [x] bulky-create with ignore_conflicts
  - [x] custom pagination and LimitOffsetPagination
  - [x] DEFAULT_THROTTLE_CLASSES and custom ip blocker
  - [x] django_filters used to get a list of unread messages
  - [x] use TrigramSimilarity/SearchRank/SearchVector for search
   
- ------------------------------------------------------------------------------------

 - [x] Implemented celery-task    
 - [x] Used Signals post-save / Used custom signal
 - [x] API to get a summary of the room and send it as a message -> Used AI (LANGCHAIN)

-  --------------------------------------------------------------------------------------------
 
 - [x] Used swagger for documentation
 - [x] Used django-debug-toolbar
 - [X] Used admin custom(  
         *) Customize Admin Site with ModelAdmin Class  
         *) Use list_select_related           
         *) List Display Custom Fields   
         *) Search field and filter field  
         *) Use custom action
      
-  --------------------------------------------------------------------------------------------

 - [x] use RunPython / RunSql for dataMigration
 - [x] TimescaleDb and tablespace to store logs in database
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

- [x] --------------------------------------------------------------------------------------------


 - [x] TruncDay
    
    ```commandline
    TruncDay is a database function provided by Django's ORM that truncates a 
    date and time to the "day" level, effectively removing any more granular time information such as hours, minutes, and seconds. 
    This is part of Django's suite of database functions that allow you to 
    manipulate date and time fields directly in your queries, which can be very useful for grouping records by day or for performing date-based aggregation directly in the database.
    ```
   ```commandline
    from django.db.models.functions import (
             TruncDate,
             TruncDay,
             TruncHour,
             TruncMinute,
             TruncSecond,
         )
    ```
   
-  --------------------------------------------------------------------------------------------
