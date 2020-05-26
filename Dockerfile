# pull official base image
FROM python:3.6

# set working directory
WORKDIR /server

# copy project file to working dir
COPY . .
# clear the resources directory, for testing reasons
RUN cd /server && rm -rf /resources

# go to project dir and install dependencies
RUN cd /server && pip install -r requirements.txt

EXPOSE 443

CMD ["python3" ,"/server/app.py"]
