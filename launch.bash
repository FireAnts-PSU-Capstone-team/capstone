#!/bin/bash

# This script is used to build, test, and run the container.

CURRENT_FILE_FOLDER_NAME=$(basename $(dirname $(realpath $0)))

if [[ $(dirname $0) != '.' ]]
then
    cd $(dirname $0)
fi

function usage() {
    echo "Usage: "
    echo "  bash $0 clean          delete any existing version of the web server image"
    echo "  bash $0 run            run the program"
    echo "  bash $0 stop           stop the program"
    echo "  bash $0 rebuild        remove all data and rebuild the program"
    echo "  bash $0 rebuild-db     remove only DB data and re-run the program"
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

# count # of row of records in table
function count_rows() {
    rows=$(($(echo "$1" | wc -l) - 2)) 
    if [[ ${rows} -gt  0 ]]
    then
        echo $(($rows/$2))
    else
        echo 0
    fi
}


# perform some tests after building the program to ensure the program is correct
function run_test() {

    # config variables
    server_port='800'
    tables=('metadata' 'intake' 'txn_history')
    primary_table='intake'
    record_row=(9 29 38)
    testing_spreadsheet='resources/sample-extension.xlsx'
    test_row='resources/sample-row-1.json'
    db_name=$(cut -f 3 -d ' ' db/database.ini  | sed -n '2p')
    db_user=$(cut -f 3 -d ' ' db/database.ini  | sed -n '3p')
    db_pass=$(cut -f 3 -d ' ' db/database.ini  | sed -n '4p')


    # check if can use the default credential to connect to postgres DB
    if [[ -z $(psql postgresql://${db_user}:${db_pass}@localhost:5432/postgres -c '') ]]
    then
        echo "1. DB connection successful."
    else
        echo "1. ERROR: DB connection unsuccessful."
        exit
    fi

    # check if the target DB was created inside the postgres DB
    out=$(psql postgresql://${db_user}:${db_pass}@localhost:5432/postgres -lA | grep "${db_name}|")

    if [[ -z ${out} ]]
    then
        echo "2. ERROR: DB not created."
        exit
    else
        echo "2. DB \"${db_name}\" created."
    fi

    # check if required tables created in the DB
    out=$(psql postgresql://${db_user}:${db_pass}@localhost:5432/${db_name} -Ac '\d')

    for i in "${tables[@]}"
    do
        if [[ -z "$(echo ${out} | grep "${i}")" ]]
        then
            echo "3. ERROR: table \"${i}\" not created."
            exit
        else
            echo "3. Table \"${i}\" created."
        fi
    done

    # check if server is working
    out=$(curl -s http://localhost:${server_port})
    if [[ "${out}" == "\"Hello World\"" ]]
    then
        echo "4. Web server is up."
    else
        echo "4. ERROR: Web server is not working."
        exit
    fi

    # testing spreadsheet IO
    out=$(curl -s localhost:${server_port}/list?table=${tables[0]})
    if [[ "${out}" =~ \[.*\] ]]
    then
        echo "5. Testing spreadsheet uploading."
        echo "5. Before uploading:"

        c=0
        for i in "${tables[@]}"
        do
            out=$(curl -s localhost:${server_port}/list?table=${i})
            echo "5. Table \"${i}\" has $(count_rows "$out" ${record_row[${c}]}) rows (first 10 lines):"
            echo "$out" | head -10
            ((c++))
        done

        echo "5. Loading spreadsheet \"${testing_spreadsheet}\""
        
        out=$(curl -X POST -s --form "file=@${testing_spreadsheet}" http://localhost:${server_port}/load)
        if [[ -n "$(echo ${out} | grep "File processed successfully")" ]]
        then
            echo "5. After uploading:"

            c=0
            for i in "${tables[@]}"
            do
                out=$(curl -s localhost:${server_port}/list?table=${i})
                echo "5. Table \"${i}\" has $(count_rows "$out" ${record_row[${c}]}) rows (first 10 lines):"
                echo "$out" | head -10
                ((c++))
            done
        else
            echo "5. ERROR: Failed to load file."
            exit
        fi
    else
        echo "5. ERROR: Web server can't list tables."
        exit
    fi

    echo "6. Testing row insertion."
    out=$(curl -X PUT localhost:${server_port}/load?table=${primary_table} -d @${test_row} -H "Content-Type: application/json")
    if [[ -n "$(echo ${out} | grep 'PUT complete')" ]]
    then
        echo "Row insertion ran successfully."
    else
        echo ${out}
        exit
    fi

    echo ">>>> End testing."
}

# accept an argument to perform action, print usage if nothing given

if [[ $1 == "clean" ]]; then
    sudo docker image rm flask-server:v1 >/dev/null 2>&1

elif [[ $1 == "run" ]]; then

    # if the image doesn't exist (or we've just deleted it), build it fresh
    sudo docker image inspect flask-server:v1 >/dev/null 2>&1
    [[ $? != 0 ]] && echo "Image does not exist; building image" && sudo docker build -t flask-server:v1 .
    sudo chown -R 999:root configs/
    sudo chmod 777 configs/
    sudo chmod 600 configs/*

    # bring up the container
    sudo docker-compose up
    # TODO: refactor duplicated code
    # TODO: automatically catch error requiring 'postgresql stop'; execute that and retry

elif [[ $1 == "stop" ]]; then

    server_container="${CURRENT_FILE_FOLDER_NAME}_web_1" 
    db_container="${CURRENT_FILE_FOLDER_NAME}_db_1"

    # stop the containers
    sudo docker stop ${server_container} ${db_container}

elif [[ $1 == "rebuild" ]]; then
    # rebuild everything
    sudo rm -r pgdata
    sudo docker image rm -f flask-server:v1
    sudo docker build -t flask-server:v1 .
    sudo chown -R 999:root configs/
    sudo chmod 777 configs/
    sudo chmod 600 configs/*
    sudo docker-compose up
    
elif [[ $1 == "rebuild-db" ]]; then

    # clear DB data and re-run the program
    sudo rm -r pgdata
    sudo docker-compose up

elif [[ $1 == "test" ]]; then
    run_test
else
    usage
    exit 0
fi
