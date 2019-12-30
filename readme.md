#### Description
A complete web application that gathers data from a multipart form on frontend, then parses it in the backend, and then uploads to Jenkins

- Validates data on the frontend including the uploaded files structure

- Uses asyc server based on aiohttp

- Uploads data to Jenkins in a separate thread taking data from the queue

#### Setup
Use python 3.7.4 or higher to run setup.py and install dependencies:

    python3 setup.py install 


#### Run
Use python 3.7.4 to run main.py:

    python3 main.py