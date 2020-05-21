# Capstone Project
 
## Team members:
- Andrew Haley
- Lawrence Gunnell
- Connor Kazmierczak
- Ha Ly
- Sean Mitchell
- Kanra Su
- Alicja Wolak


## Startup

There is a launch script that will handle bringing up the containers and performing cleanup on exit. To build and launch 
the project, type `bash launch.bash build`.\
If a current image of the project already exists locally, you can instead run the existing image by typing `bash launch.bash run` instead.

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


## launch.bash Usage

In project folder:

``` sh
bash launch.bash clean          delete any existing version of the web server image
bash launch.bash run            run the program
bash launch.bash stop           stop the program
bash launch.bash build          remove all data and rebuild the program
bash launch.bash rebuild-db     remove only DB data and re-run the program
bash launch.bash test           test the program (for a fresh/new built program)
```

## Troubleshooting
If you get an error when running `sudo docker-compose up` indicating that port 5432 (Postgres) is already in use, you need to stop postgresql and try again:\
`sudo service postgresql stop`\
\
If you attempt a request and receive a reply regarding unverified certificates, repeat the command 
with `-k` provided as an additional argument.

## Interacting with the server
You can open a browser and go to [https://localhost:443](https://localhost:443) to connect to the running API. From here, you can hit any of the endpoints specified in the `server.py` file.

You can also query the API from the command line, using `curl`: 

&emsp;List the contents of the `intake` table: \
&emsp;&emsp;`curl -k https://localhost:443/list?table=intake` \
&emsp;Post the `sample.xlsx` file to the `/load` endpoint: \
&emsp;&emsp;`curl -k --form -X POST "file=@resources/sample.xlsx" https://localhost:443/load` \
&emsp;Add a single row, as contained in the `sample-row-1.json` file: \
&emsp;&emsp;`curl -k -X PUT https://localhost:443/load?table=intake -d @resources/sample-row-1.json -H "Content-Type: application/json"` \
&emsp;List entries from the `intake` table, but only the submission date and MRL fields: \
&emsp;&emsp;`curl -k "https://localhost:443/list?table=intake&column=submission_date+mrl"` \
&emsp;List entries from the database where results are filtered based on a JSON-structured query file: \
&emsp;&emsp;`curl -k -X POST https://localhost:443/list -d @resources/test-query-and-1.json -H "Content-Type: application/json"` \
&emsp;Delete a row of the `intake` table: \
&emsp;&emsp;`curl -k "https://localhost:443/delete?table=intake&row=2"`

