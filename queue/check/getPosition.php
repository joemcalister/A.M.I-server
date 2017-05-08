<?php

    // print errors for debug
    //ini_set('display_errors', 1);
    //ini_set('display_startup_errors', 1);
    //error_reporting(E_ALL);
    
    // note json returns
    header('Content-Type: application/json');

    // check for the correct arguments
    $unsafe_userid = $argv[1];
    if (strlen($unsafe_userid) == 0)
    {
        // no user id included -- end.
        die("No user id provided");
        
    }else {
        // import database credentials
        include_once("/var/www/api.joemcalister.com/html/ami/queue/credentials/cred.php");

        // create connection -- using cred not included in git
        $conn = new mysqli($DBServer, $DBUser, $DBPass, $DBName);

        // check for correct connection
        if ($conn->connect_error) {
            // send error to user
            die("Error connecting to database");
        } 

        // get safe id
        $SAFEUSERID = $conn->real_escape_string($unsafe_userid);
        
        // get the details for the required user
        $sql = "SELECT * FROM `users` WHERE `queuing`=1";
        $result = $conn->query($sql);

        if ($result->num_rows > 0) {
            // there was a result -- it will be the user, just 1 result
            $num = 1;
            while($row = $result->fetch_assoc()) {
                // echo the row
                if ($row["phone_number"]==$unsafe_userid)
                {
                    $conn->close();
                    die("$num");
                }else {
                    $num++;
                }
            }
            
            echo("None");
            
        } else {
            // display error, showing no results were found
            echo("None");
        }

        // close the connection
        $conn->close();
    }


?>