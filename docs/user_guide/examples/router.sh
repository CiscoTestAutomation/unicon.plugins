#!/bin/bash
hostname="sim-router"
disable_prompt="$hostname>"
enable_prompt="$hostname#"
config_prompt="$hostname(config)#"
echo "Trying X.X.X.X ...
Escape character is '^]'.
Press enter to continue ..."
read escape_char

if [[ $escape_char == "" ]]
then
    echo -n "username: "
    read username
    if [[ $username == "admin" ]]
    then
        echo -n "password: "
        read -s password
        if [[ $password == "lab" ]]
        then
            echo
            #echo -n "$disable_prompt"
        else
            echo "bad password"
            exit 1
        fi
    else
        echo "wrong username"
        exit 1
    fi
fi

prompt=$disable_prompt
while true
do
    echo -n $prompt
    read resp
    # enable command
    if [[ $resp == "enable" || $resp == "en" ]]
    then
        password=""
        echo -n "password: "
        read  password
        if [[ $password == "lablab" ]]
        then
            prompt=$enable_prompt
        else
            echo "Bad Password"
        fi
    # show clock command
    elif [[ $resp == "show clock" || $resp == "sh clock" ]]
    then
        echo $(date)

    # config mode.
    elif [[ $resp == "config" || $resp == "config term" ]]
    then
        # check if we are in enable mode
        if [[ $prompt == $enable_prompt ]]
        then
            echo -n "Configuring from terminal, memory, or network [terminal]? "
            read resp
            if [[ $resp == "" ]]
            then
                prompt=$config_prompt
            fi
        else
            echo "you need to be in enable mode"
        fi
    # config end
    elif [[ $resp == "end" ]]
    then
        # check if are in config mode
        if [[ $prompt == $config_prompt ]]
        then
            prompt=$enable_prompt
        else
            echo "you need to be in config mode"
        fi
    # going to disable mode.
    elif [[ $resp == "disable" ]]
    then
        # check if we are in enable mode first
        if [[ $prompt == $enable_prompt ]]
        then
            prompt=$disable_prompt
        else
            echo "you need to be in enable mode"
        fi
    fi
done
