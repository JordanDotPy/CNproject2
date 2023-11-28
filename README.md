# CNproject2

## Team 
Jordan Shaheen
Chris Trentmen
Simon Feist

## Instructions
In one terminal, run the server Python file with python3 server2.py.
In another terminal, run the client Python file python3 client.py.
Add more terminals running the client Python files to add more users.

## Project Description
When you first run the client after you already started the server, you are first prompted to enter an origional username, if username is not origional you will be prompt to re-enter one.  Once you created an origional username, you are then placed within the public chat where every active user can see your messages within the it, and you can retrieve and post public chats whenever (Part1).  Also, once you join you will be prompted the proper keywords to join a group, leave a group, post to the public chat, retrieve a message from the public chat, post to a group, and retrieve a group message.  Additionally, you can also join up to 5 groups that have been statically created on the server initialization.  Using the proper keywords, you can post to that group where only the users in that group can see it, and you can retieve messages from that group as well (part2).  If at anytime you try to preform an action with improper keywords, the server will recognize this and state it as an improper message format, and resend all the proper ways to use the keywords for the Message Board.

## Major Issues
Initially wrote the client side to be Java, but this caused a lot of bugs with the server sending messages back to the client only after the client senty a message to the server.  This caused the server response to any message board actions to be a step behind the real time execution.  To solve this we just switched the client to Python code which instantly solved the issue.

## Minor Issue?
Sometimes when testing the code after shutting down all clients and server and restarting it after changes, the server would throw an error that the port used is already in use, when in reality no one was already on the port.  To fix this, we simply incremented the port from 8888 to 8889 or vise versa.  However, this problem only seemed to happen to Jordan, but if this issue happens, just increment or decrement the port number by 1.

## Packages Used
Only Socket, Threading, and datetime are used within this project, so there may not need to be any pip install commands for you to run this project.
