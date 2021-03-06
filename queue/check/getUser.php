<?php

    // print errors for debug
    //ini_set('display_errors', 1);
    //ini_set('display_startup_errors', 1);
    //error_reporting(E_ALL);
    
    // note json returns
    header('Content-Type: application/json');

    // check for the correct get requests
    $unsafe_userid = $_GET["id"];
    if (strlen($unsafe_userid) == 0)
    {
        // no user id included -- end.
        die(json_encode(array("success"=>0, "error_message"=>"User ID must be declared. [Client error]")));
        
    }else {
        // import database credentials
        include_once("../credentials/cred.php");

        // create connection -- using cred not included in git
        $conn = new mysqli($DBServer, $DBUser, $DBPass, $DBName);

        // check for correct connection
        if ($conn->connect_error) {
            // send error to user
            die(json_encode(array("success"=>0, "error_message"=>"Error connecting to database. [Internal error]")));
        } 

        // get safe id
        $SAFEUSERID = $conn->real_escape_string($unsafe_userid);
        
        // get the details for the required user
        $sql = "SELECT * FROM `active-users` WHERE `userid`=$SAFEUSERID";
        $result = $conn->query($sql);

        if ($result->num_rows > 0) {
            // there was a result -- it will be the user, just 1 result
            while($row = $result->fetch_assoc()) {
                // echo the row
                echo(json_encode(array("success"=>1, "payload"=>$row)));
            }
            
        } else {
            // display error, showing no results were found
            echo(json_encode(array("success"=>0, "error_message"=>"No user with that ID was found.")));
        }

        // close the connection
        $conn->close();
    }


?>