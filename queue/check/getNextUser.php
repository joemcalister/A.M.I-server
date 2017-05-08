<?php

    // print errors for debug
    //ini_set('display_errors', 1);
    //ini_set('display_startup_errors', 1);
    //error_reporting(E_ALL);
    
    // note json returns
    header('Content-Type: application/json');

    // import database credentials
    include_once("../credentials/cred.php");

    // import sms basic class
    include_once("../../texting/include.php");

    // create connection -- using cred not included in git
    $conn = new mysqli($DBServer, $DBUser, $DBPass, $DBName);

    // check for correct connection
    if ($conn->connect_error) {
        // send error to user
        die(json_encode(array("success"=>0, "error_message"=>"Error connecting to database. [Internal error]")));
    } 

    // get the details for the required user
    $sql = "SELECT * FROM `users` WHERE `queuing`='1' LIMIT 1";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        // there was a result -- it will be the user, just 1 result
        while($row = $result->fetch_assoc()) {
            // grab the script for the user
            echo file_get_contents("../../data/users/".strtolower($row['username'])."/data/script.txt");
            
            // update the sql to show that this user is now
            $sql = "UPDATE `users` SET `active`='1', `queuing`='0' WHERE `user_id`='".$row['user_id']."'";
            $result = $conn->query($sql);
            
            // send the message to the user saying the show is about to start
            sendMessage("It's time! The piece is about to start.", $row['phone_number']);
        }

    } else {
        // display error, showing no results were found
        echo(json_encode(array("success"=>0, "error_message"=>"No users are currently waiting.")));
        
        // we still might need to update some records, for example if someone was just in active mode, they are now finished
        $sql = "SELECT * FROM `users` WHERE `active`='1'";
        $result = $conn->query($sql);

        if ($result->num_rows > 0) {
            // there was a result -- it will be the user, just 1 result
            while($row = $result->fetch_assoc()) {
                // send them a text saying thank you for watching
                
                // send the message to the user saying the show is about to start
                sendMessage("Thanks for visiting. For more information about A.M.I and the artist behind the piece visit https://joemcalister.com. If you want to have another go just text me hi!", $row['phone_number']);
                
                $sql = "UPDATE `users` SET `active`='0', `dead`='1' WHERE `user_id`='".$row["user_id"]."'";
                $result = $conn->query($sql);
            }
        }
    }

    // close the connection
    $conn->close();


?>