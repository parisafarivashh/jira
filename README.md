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



  - [x] login/signin --> with jwt
  - [x] models inherits from basemodel --> baseModel is abstract model that has two filed
  - [x] models inherits from soft_delete --> softDelete is abstract model that has removed_at filed
  - [x] if project created --> privateRoom, publicRoom created for project --> message "created" sended to publicRoom
  - [x] The user could seen message --> if member is a member of room then latest-seen-message updated
  - [x] Send message --> when sending a message to the room... previous messages are seen.. 
    
  - [x] Used extra action of ViewSets (Added Custom endpoint to seen message and edit message)
  - [x] bulky-create with ignore_conflicts
  - [x] custom pagination and LimitOffsetPagination
  - [x] django_filters used to get list unread messages
 
 
