# pull official base image
FROM python:3.6

# set working directory
WORKDIR /server

# copy project file to working dir
COPY . .

# go to project dir and install dependencies
RUN cd /server && pip install -r requirements.txt

EXPOSE 800

CMD [ "python3" ,"/server/server.py"]
