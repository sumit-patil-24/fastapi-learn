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

Distroless images in Docker typically provide a default non-root user to enhance security by adhering to the principle of least privilege. 
- Distroless image already comes with a user named nonroot (with UID 65532) built into it.

## summery
- use non-root user
- use multistage
- use .dockerignore
- use right commands to run
- use distroless image


command:
docker run \
  --read-only \
  --tmpfs /tmp \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --pids-limit 100 \
  --memory 256m \
  --cpus 0.5 \
  -p 3000:3000 \
  secure-app

## note: 
    - if you build docker image using distroless images then that containers will not provide shell.
    