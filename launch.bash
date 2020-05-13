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
    echo "  bash $0 build          remove all data and rebuild the program"
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
    server_port='443'
    tables=('metadata' 'intake' 'txn_history' 'archive')
    primary_table='intake'
    record_row=(9 29 38)
    prefixed_host='https://localhost'
    self_signed=' -k'
    testing_spreadsheet='resources/sample-extension.xlsx'
    test_row='resources/sample-row-1.json'
    # read from database.ini
    source <(grep = "db/database.ini")
    db_name=$dbname
    db_user=$user
    db_pass=$password

    if [[ -z $(psql postgresql://${db_user}:${db_pass}@localhost:5432/postgres?sslmode=require -c '') ]]
    then
        echo "1. DB connection successful."
    else
        echo "1. ERROR: DB connection unsuccessful."
        exit
    fi

    # check if the target DB was created inside the postgres DB
    out=$(psql postgresql://${db_user}:${db_pass}@localhost:5432/postgres?sslmode=require -lA | grep "${db_name}|")

    if [[ -z ${out} ]]
    then
        echo "2. ERROR: DB not created."
        exit
    else
        echo "2. DB \"${db_name}\" created."
    fi

    # check if required tables created in the DB
    out=$(psql postgresql://${db_user}:${db_pass}@localhost:5432/${db_name}?sslmode=require -Ac '\d')

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
    out=$(curl -s ${prefixed_host}:${server_port}${self_signed})
    if [[ ${out} == "\"Hello World\"" ]]
    then
        echo "4. Web server is up."
    else
        echo "4. ERROR: Web server is not working."
        exit
    fi

    # testing spreadsheet IO
    out=$(curl -s ${prefixed_host}:${server_port}/list?table=${tables[0]}${self_signed})
    if [[ "${out}" =~ \[.*\] ]]
    then
        echo "5. Testing spreadsheet uploading."
        echo "5. Before uploading:"

        c=0
        for i in "${tables[@]}"
        do
            out=$(curl -s ${prefixed_host}:${server_port}/list?table=${i}${self_signed})
            echo "5. Table \"${i}\" has $(count_rows "$out" ${record_row[${c}]}) rows (first 10 lines):"
            echo "$out" | head -10
            ((c++))
        done

        echo "5. Loading spreadsheet \"${testing_spreadsheet}\""
        
        out=$(curl -X POST -s --form "file=@${testing_spreadsheet}" ${prefixed_host}:${server_port}/load${self_signed})
        echo ${out} | grep "File processed successfully" > /dev/null
        if [[ $? == 0 ]]
        then
            echo "5. After uploading:"

            c=0
            for i in "${tables[@]}"
            do
                out=$(curl -s ${prefixed_host}:${server_port}/list?table=${i}${self_signed})
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
    out=$(curl -s -X PUT ${prefixed_host}:${server_port}/load?table=${primary_table} -d @${test_row} -H "Content-Type: application/json"${self_signed})
    if [[ -n "$(echo ${out} | grep 'PUT complete')" ]]
    then
        echo "Row insertion ran successfully."
    else
        echo ${out}
        exit
    fi

    echo ">>>> End testing."
}

function run() {

    # change permissions of SSL config files
    sudo chown -R 999:root configs/
    sudo chmod 777 configs/
    sudo chmod 600 configs/*

    # if the image doesn't exist (or we've just deleted it), build it fresh
    sudo docker image inspect flask-server:v1 >/dev/null 2>&1
    [[ $? != 0 ]] && echo "Image does not exist; building image" && sudo docker build -t flask-server:v1 .

    # launch and check for 'port in use' error
    echo "Launching container"
    sudo docker-compose up
#    if [[ $? == 1 ]]; then
#        if [[ $2 == "retry" ]]; then
#            echo "Attempted to re-run program, but postgresql service could not be stopped. Stop the service and try again."
#            exit 1
#        else
#            echo "Stopping postgresql service."
#            sudo service postgresql stop
#            echo "Retrying."
#            run "retry"
#        fi
#    fi
}

function clean() {
    sudo rm -rf pgdata
    sudo docker image rm flask-server:v1 >/dev/null 2>&1
}

# accept an argument to perform action, print usage if nothing given

if [[ $1 == "clean" ]]; then
    clean

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

elif [[ $1 == "build" ]]; then
    clean
    run
    
elif [[ $1 == "rebuild-db" ]]; then
    # clear DB data and re-run the program
    sudo rm -r pgdata
    run

elif [[ $1 == "test" ]]; then
    run_test
else
    usage
    exit 0
fi
