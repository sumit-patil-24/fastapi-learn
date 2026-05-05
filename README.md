# fastapi-learn

configured app to use .env file.

added /crash route which will help to crash your container or application.

using root user is not secure so i used this 2 commands to secure container:

## RUN groupadd -r appuser && useradd -r -g appuser appuser
->here "groupadd -r appuser" creates new group, -g appuser: This assigns the new user to the group we just created.
The final appuser is the actual name of the new user. 

## USER appuser
->It tells Docker that every command after this line (specifically your CMD that starts the server) should be run by appuser instead of root.

in a secure container i even not able to create any file.