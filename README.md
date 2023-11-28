# CNproject2

## Team 
Jordan Shaheen
Chris Trentmen
Simon Feist

## Instructions
In one terminal, run the server Python file with python3 server2.py.
In another terminal, run the client Python file python3 client.py.
Add more terminals running the client Python files to add more users.

## Major Issues
Initially wrote the client side to be Java, but this caused a lot of bugs with the server sending messages back to the client only after the client senty a message to the server.  This caused the server response to any message board actions to be a step behind the real time execution.  To solve this we just switched the client to Python code which instantly solved the issue.

## Minor Issue?
Sometimes when testing the code after shutting down all clients and server and restarting it after changes, the server would throw an error that the port used is already in use, when in reality no one was already on the port.  To fix this, we simply incremented the port from 8888 to 8889 or vise versa.  However, this problem only seemed to happen to Jordan, but if this issue happens, just increment to decrement the port number by 1.

## Packages Used
Only Socket, Threading, and datetime are used within this project, so there may not need to be any pip install commands for you to run this server.
