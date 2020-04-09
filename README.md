# Capstone Project
 
## Team members:
- Andrew Haley
- Lawrence Gunnell
- Connor Kazmierczak
- Ha Ly
- Sean Mitchell
- Huanhua Su
- Alicja Wolak


## Startup

There is a launch script that will handle bringing up the containers and associated cleanup. To bring up the project, type `bash launch.bash`.\
If you have changed the project contents recently and wish to rebuild the Docker image rather than use the cached one, use `bash launch.bash clean` instead.

### If you prefer to run the commands manually

Delete existing (cached) Docker image: `sudo docker image rm flask-server:v1` \
Build flask server image (in project folder): `sudo docker build -t flask-server:v1 .`\
Compose and run server: `sudo docker-compose up`\
                        `sudo docker-compose up -d`       # run in background\
Stop running server: `ctrl-c`

If run in background:
``` sh
sudo docker ps
sudo docker stop <server-container> <db-container>
```
Remove built server and PostgreSQL DB containers: `sudo docker-compose down`


## Troubleshooting
If you get an error when running `sudo docker-compose up` indicating that port 5432 (Postgres) is already in use, you need to stop postgresql and try again:\
`sudo service postgresql stop`

## Interacting with the server
You can open a browser and go to [http://localhost:80](http://localhost:80) to connect to the running API. From here, you can hit any of the endpoints specified in the `server.py` file.

You can also query the API from the command line, using `curl`.\
List the contents of the `test` database: `curl http://localhost:80/list?table=test`\
Post the `Lists.xlsx` file to the `/file` endpoint: `curl -X POST -F filename="files/Lists.xlsx" http://localhost:80/file`
