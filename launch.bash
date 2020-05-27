#!/bin/bash

# This script is used to build, test, and run the container.

CURRENT_FILE_FOLDER_PATH=$(dirname $(realpath $0))
CURRENT_FILE_FOLDER_NAME=$(basename ${CURRENT_FILE_FOLDER_PATH})
USER_CURRENT_PATH=$(pwd)
db_container="capstone_db_1"
web_container="capstone_web_1"
server_port=443
# defines dbname, user, password, port
source <(grep = "kanabi/db/database.ini")

if [[ $(dirname $0) != '.' ]]
then
    cd $(dirname $0)
fi

function usage() {
    echo "Usage: "
    echo "  bash $0 clean                                     remove all data and project-specific Docker images"
    echo "  bash $0 run                                       build and run the program"
    echo "  bash $0 stop                                      stop the program"
    echo "  bash $0 rebuild                                   remove all data and rebuild the program"
    echo "  bash $0 rebuild-db                                remove only DB data and re-run the program"
    echo "  bash $0 test                                      test the program (for a freshly built program)"
    echo "  bash $0 backup <path/to/save>                     backup current DB to an external file"
    echo "                                                    if path not provided, save in current directory as <current_date>.sql"
    echo "  bash $0 restore <filename>                        restore DB from an external file"
    echo "  bash $0 backup-schedule <month|week|day> [path]   schedule regular backups at specified time intervals"
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
    tables=('metadata' 'intake' 'txn_history' 'archive')
    primary_table='intake'
    record_row=(9 29 38)
    prefixed_host='https://localhost'
    self_signed=' -k'
    testing_spreadsheet='kanabi/resources/sample-extension.xlsx'
    test_row='kanabi/resources/sample-row-1.json'

    if [[ -z $(psql postgresql://${user}:${password}@localhost:5432/postgres?sslmode=require -c '') ]]
    then
        echo "1. DB connection successful."
    else
        echo "1. ERROR: DB connection unsuccessful."
        exit
    fi

    # check if the target DB was created inside the postgres DB
    out=$(psql postgresql://${user}:${password}@localhost:5432/postgres?sslmode=require -lA | grep "${dbname}|")

    if [[ -z ${out} ]]
    then
        echo "2. ERROR: DB not created."
        exit
    else
        echo "2. DB \"${dbname}\" created."
    fi

    # check if required tables created in the DB
    out=$(psql postgresql://${user}:${password}@localhost:5432/${dbname}?sslmode=require -Ac '\d')

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
    if [[ ${out} =~ .*"Hello World".* ]]
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
    sudo chown -R 999:root kanabi/configs/
    sudo chmod 777 kanabi/configs/
    sudo chmod 600 kanabi/configs/*

    # if the image doesn't exist (or we've just deleted it), build it fresh
    sudo docker image inspect flask-server:v1 >/dev/null 2>&1
    [[ $? != 0 ]] && echo "Image does not exist; building image" && sudo docker build -t flask-server:v1 .

    echo "Launching container"
    sudo docker-compose up
}

function clean() {
    sudo rm -rf kanabi/pgdata
    sudo docker image rm flask-server:v1 >/dev/null 2>&1
}

# TODO: update so this works
function backup() {

    out_file_path=''

    if [[ -z $1 ]]
    then
        da=$(date +%Y%m%d%H%M%S)
        out_file_path="${USER_CURRENT_PATH}/${da}.sql"
    else
        if [[ ${1:0:1} == '/' ]]
        then
            out_file_path="${1}"
        else
            out_file_path="${USER_CURRENT_PATH}/${1}"
        fi
    fi

    sudo docker exec -it ${db_container} pg_dump -d postgresql://${user}:${password}@localhost:5432/${dbname} > $out_file_path
    if [[ $? == 0 ]]; then
        echo "Backup successful to file: ${out_file_path}"
    else
        echo "Backup failed"
    fi
}

function restore() {
    in_file_path=''

    if [[ -z $1 ]]
    then
        echo "Error: please supply an external sql file."
        exit
    else
        if [[ ${1:0:1} == '/' ]]
        then
            in_file_path=$1
        else
            in_file_path="${USER_CURRENT_PATH}/${1}"
        fi

        ls $in_file_path > /dev/null 2> /dev/null
        if [[ $? != 0 ]]
        then
            echo "File ${in_file_path} does not exist."
            exit 1
        fi
    fi

    echo "Restoring DB from file (${in_file_path})..."

    # remove current DB stuffs
    psql postgresql://${user}:${password}@localhost:5432/${dbname} < db/db-remove.sql

    # execute backup .sql file
    psql postgresql://${user}:${password}@localhost:5432/${dbname} < ${in_file_path}

    [[ $? == 0 ]] && echo "Restored successfully."
}

function backup-schedule() {
    cmd="bash ${CURRENT_FILE_FOLDER_PATH}/launch.bash backup ${2}"
    comment=''

    if [[ $1 == 'week' ]]
    then
        cmd="0 0 * * 0 ${cmd}"
        comment="Scheduled to backup every week Sunday at 00:00 AM."
    elif [[ $1 == 'month' ]]
    then
        cmd="0 0 1 * * ${cmd}"
        comment="Scheduled to backup every Month first day at 00:00 AM."
    else
        # every day
        cmd="0 0 * * * ${cmd}"
        comment="Scheduled to backup every day at 00:00 AM."
    fi

    echo $comment
    crontab -l | sed '/\/launch.bash backup/d' | { cat; echo "${cmd} # ${comment}"; } | crontab - > /dev/null
}

# accept an argument to perform action, print usage if nothing given

if [[ $1 == "clean" ]]; then
    clean

elif [[ $1 == "run" ]]; then
    run

elif [[ $1 == "stop" ]]; then

    server_container="${CURRENT_FILE_FOLDER_NAME}_web_1"
    db_container="${CURRENT_FILE_FOLDER_NAME}_db_1"

    # stop the containers
    sudo docker stop ${server_container} ${db_container}

elif [[ $1 == "rebuild" ]]; then
    clean
    run
    
elif [[ $1 == "rebuild-db" ]]; then
    # clear DB data and re-run the program
    sudo rm -r kanabi/pgdata
    run

elif [[ $1 == "test" ]]; then
    run_test

elif [[ $1 == "backup" ]]; then
    backup $2

elif [[ $1 == "restore" ]]; then
    restore $2

elif [[ $1 == "backup-schedule" ]]; then
    backup-schedule $2 $3

else
    usage
    exit 0
fi
