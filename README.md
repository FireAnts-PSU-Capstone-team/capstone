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
the project, type `bash launch.bash run`.
 

### If you prefer to run the commands manually

`sudo docker image rm flask-server:v1` &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;&nbsp;Delete existing (cached) Docker image 

`sudo docker build -t flask-server:v1 .`&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Build flask server image (in project folder):

`sudo docker-compose up` &ensp;&nbsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Compose and run server 

`sudo docker-compose up -d`        &nbsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Run in background

`ctrl-c` &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Stop running server 

`sudo docker-compose down` &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;&nbsp;Remove built server and PostgreSQL DB containers

If run in background, stop containers with:
``` sh
sudo docker ps
sudo docker stop <server-container> <db-container>
```


## launch.bash Usage

In project folder:

``` sh
bash launch.bash clean                                     remove all data and project-specific Docker images
bash launch.bash run                                       build and run the program
bash launch.bash stop                                      stop the program
bash launch.bash rebuild                                   remove all data and rebuild the program
bash launch.bash rebuild-db                                remove only DB data and re-run the program
bash launch.bash test                                      test the program (for a freshly built container)
bash launch.bash backup [path]                             backup current DB to an external file
                                                           if path not provided, save in current directory as <current_date>.sql
bash launch.bash restore <filename>                        restore DB from an external file
bash launch.bash backup-schedule <month|week|day> [path]   schedule regular backups at specified time intervals
```

## Troubleshooting
If you get an error when running `sudo docker-compose up` indicating that port 5432 (Postgres) is already in use, you need to stop postgresql and try again:
`sudo service postgresql stop`

If you attempt a request and receive a reply regarding unverified SSL certificates, repeat the command 
with `-k` provided as an additional argument.

## Interacting with the server
You can open a browser and go to [https://localhost:443](https://localhost:443) to connect to the running API. From here, 
you can hit any of the endpoints specified in the `server.py` file.

You can also query the API from the command line, using `curl`: 
&emsp; 
&emsp;
> /list

**List the contents of the `intake` table:** 
```
curl -k https://localhost:443/list?table=intake -b COOKIE_FILE -c COOKIE_FILE
```

**List entries from the `intake` table, but only the submission date and MRL fields:**
```
curl -k "https://localhost:443/list?table=intake&column=submission_date+mrl" -b COOKIE_FILE -c COOKIE_FILE
```

**List entries from the database where results are filtered based on a JSON-structured query file:**
```
curl -k -X POST https://localhost:443/list -d @resources/test-query-and-1.json -H "Content-Type: application/json" -b COOKIE_FILE -c COOKIE_FILE
``` 
&emsp; 

> /load

**Post the `sample.xlsx` file to the `/load` endpoint:**
```
curl -k -X POST --form "file=@resources/sample.xlsx" https://localhost:443/load?table=intake -b COOKIE_FILE -c COOKIE_FILE
```

**Add a single row, as contained in the `sample-row-1.json` file:**
```
curl -k -X PUT https://localhost:443/load?table=intake -d @resources/sample-row-1.json -H "Content-Type: application/json" -b COOKIE_FILE -c COOKIE_FILE
```
&emsp; 

> /update

**Update intake table on row 1, for 2 columns, in content-type of JSON:**
```
curl -d '{"row":"1", "receipt_num":200, "phone": 555555}' -H "Content-Type: application/json" -k -X POST https://localhost:443/update -b COOKIE_FILE -c COOKIE_FILE
```

**Update intake table on row 1, for 1 columns, in content-type of x-www-form-urlencoded:**
```
curl -d "row=1&cash_amount=100" -X POST -k https://localhost:443/update -b COOKIE_FILE -c COOKIE_FILE
```
&emsp; 
> /delete

**Delete the row with ID '2' from the intake table:**
```
curl -k "https://localhost:443/delete?table=intake&row=2" -b COOKIE_FILE -c COOKIE_FILE
```

**Delete multiple rows from the intake table:**
```
curl -k "https://localhost:443/delete?table=intake&row=1+2" -b COOKIE_FILE -c COOKIE_FILE
```
&emsp; 
> /export

**Export the intake table as a CSV file named 'intake.csv':**
```
curl https://localhost/export?table=intake -o intake.csv -b COOKIE_FILE -c COOKIE_FILE
```
&emsp; 
> /restore

**Restore a row 1 in the archive table back to the table it was delete from:**
```
curl -k -X PUT "https://localhost:443/restore?row=1" -b COOKIE_FILE -c COOKIE_FILE
```
&emsp;

&emsp; 
### Authentication
> /signup

**Sign up as a new user:** 
```
curl -k -X OPTIONS -H "Origin: GUI_DOMAIN" -H "Content-Type: application/json" --request POST --data '{"email":"EMAIL_ADDRESS","password":"PASSWORD","name":"True"}' https://SERVER:PORT/signup
```
&emsp; 
> /login

**Log in as an existing user:** 
```
curl -k -X OPTIONS -H "Origin: GUI_DOMAIN" -H "Content-Type: application/json" --request POST --data '{"email":"EMAIL_ADDRESS","password":"PASSWORD","remember":"True"}' -c cookie.txt https://SERVER:PORT/login
```
Note that the cookie argument is required for the server to keep track of a user's login status. 

In subsequent requests, this named cookie must be provided to the server every time using the `-b` and `-c` arguments, like so:
```
curl -X GET https://localhost/usrhello -k -b a.cookie -c a.cookie
```
`-b` uses the named cookie as input; `-c` saves any updates the server makes to that cookie. 

&emsp; 

> /logout

**Log out:** 
```
curl -k https://SERVER:PORT/logout -c test.cookie -b test.cookie
```
&emsp; 
