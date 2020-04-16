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

`sudo docker image rm flask-server:v1` &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;&nbsp;Delete existing (cached) Docker image  \
`sudo docker build -t flask-server:v1 .`&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Build flask server image (in project folder): \
`sudo docker-compose up` &ensp;&nbsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Compose and run server \
`sudo docker-compose up -d`        &nbsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Run in background\
`ctrl-c` &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Stop running server \
`sudo docker-compose down` &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;&nbsp;Remove built server and PostgreSQL DB containers

If run in background, stop containers with:
``` sh
sudo docker ps
sudo docker stop <server-container> <db-container>
```



## Troubleshooting
If you get an error when running `sudo docker-compose up` indicating that port 5432 (Postgres) is already in use, you need to stop postgresql and try again:\
`sudo service postgresql stop`

## Interacting with the server
You can open a browser and go to [http://localhost:800](http://localhost:800) to connect to the running API. From here, you can hit any of the endpoints specified in the `server.py` file.

You can also query the API from the command line, using `curl`.\
List the contents of the `intake` table: `curl http://localhost:800/list?table=intake` \
Post the `sample.xlsx` file to the `/file` endpoint: `curl -X POST http://localhost:800/load?file=sample.xlsx`
