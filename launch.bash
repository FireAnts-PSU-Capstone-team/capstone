#!/bin/bash

# This script brings up the container and shuts it down on receiving a ctrl-c kill signal.

CURRENT_FILE_FOLDER_NAME=$(basename $(dirname $(realpath $0)))


function usage() {
    echo "Usage: "
    echo "  bash $0 clean          delete any existing version of the web server image"
    echo "  bash $0 run            run the program"
    echo "  bash $0 stop           stop the program"
    echo "  bash $0 rebuid         remove all data and rebuild the program"
    echo "  bash $0 rebuid-db      remove only DB data and re-run the program"
    echo "  bash $0 test           test the program (for a fresh/new built program)"

}

# ctrl-c is used to abort a running container session. To keep the session self-contained by this script,
# we will capture the ctrl-c SIGINT signal and use it to call docker-compose down.
# That way, we do not have behavior where the script calls docker-compose up, but we have to remember
# to call docker-compose down separately.
function trap_ctrlc() {
    sudo docker-compose down
    exit 0
}
trap "trap_ctrlc" 2

# perform some tests after building the program, ensure if the program is correct
function test() {

    # a list of tables (table name) that is created & used by the program
    server_port='800'
    tables=('metadata' 'test')
    db_name=$(cut -f 3 -d ' ' database.ini  | sed -n '2p')
    db_user=$(cut -f 3 -d ' ' database.ini  | sed -n '3p')
    db_pass=$(cut -f 3 -d ' ' database.ini  | sed -n '4p')


    # check if can use the default credential to connect to postgre DB
    if [ -z $(psql postgresql://${db_user}:${db_pass}@localhost:5432/postgres -c '') ]
    then
        echo "1. DB connection succeed."
    else
        echo "1. ERROR: DB connection not work."
        exit
    fi

    # check if the target DB created inside the postgre DB
    out=$(psql postgresql://${db_user}:${db_pass}@localhost:5432/postgres -lA | grep "${db_name}|")

    if [ -z $out ]
    then
        echo "2. ERROR: DB didn't created."
        exit
    else
        echo "2. DB \"${db_name}\" created."
    fi

    # check if required tables created in the DB
    out=$(psql postgresql://${db_user}:${db_pass}@localhost:5432/${db_name} -Ac '\d')

    for i in "${tables[@]}"
    do
        if [ -z "$(echo $out | grep "${i}")" ]
        then
            echo "3. ERROR: table \"${i}\" didn't created."
            exit
        else
            echo "3. Table \"${i}\" created."
        fi
    done

    # check if server is working
    out=$(curl -s http://localhost:${server_port})
    if [ "${out}" == "Hello World" ]
    then
        echo "4. Web server is up."
    else
        echo "4. ERROR: Web server is not working."
        exit
    fi

    # testing excel file IO
    out=$(curl -s localhost:${server_port}/list?table=test)
    if [ "${out}" == "[]" ]
    then
        echo "5. Loading excel file."
        
        out=$(curl -s --form "file=@files/Lists.xlsx" http://localhost:${server_port}/file)
        if [ -n "$(echo $out | grep "\"OK\"")" ]
        then
            for i in "${tables[@]}"
            do
                echo "5. Table \"${i}\" result (first 10 lines):"
                curl -s localhost:${server_port}/list?table=${i} | head -10
                
            done

        else
            echo "5. ERROR: Failed to load file."
            exit
        fi

    else
        echo "5. ERROR: Web server can't list tables."
        exit
    fi


    echo ">>>> End testing."
}

# accept an argument to perform action, print usage if nothing given
if [[ $1 == "clean" ]]; then

    sudo docker image rm flask-server:v1

elif [[ $1 == "run" ]]; then

    # if the image doesn't exist (or we've just deleted it), build it fresh
    sudo docker image inspect flask-server:v1 >/dev/null 2>&1
    [[ $? != 0 ]] && echo "Image does not exist; building image" && sudo docker build -t flask-server:v1 .

    # bring up the container
    sudo docker-compose up

elif [[ $1 == "stop" ]]; then

    server_container="${CURRENT_FILE_FOLDER_NAME}_web_1" 
    db_container="${CURRENT_FILE_FOLDER_NAME}_db_1" 

    # stop the containers
    sudo docker stop $server_container $db_container

elif [[ $1 == "rebuild" ]]; then

    # rebuild everything
    sudo rm -r pgdata || sudo docker image rm -f flask-server || sudo docker build -t flask-server:v1 . && sudo docker-compose up
    
elif [[ $1 == "rebuild-db" ]]; then

    # clear DB data and re-run the program
    sudo rm -r pgdata && sudo docker-compose up

elif [[ $1 == "test" ]]; then
    test
else
    usage
    exit 0
fi

