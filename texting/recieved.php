<?php
// Required if your environment does not handle autoloading
require __DIR__ . '/vendor/autoload.php';

// Use the REST API Client to make requests to the Twilio REST API
use Twilio\Rest\Client;

// include the credentials for the mysql db
include_once("cred/credentials.php");

// set timeout time limit, this will still cause twilio to send error but still work
set_time_limit(3000);


// get the info from the text message
$bodyMessage = $_POST['Body'];
$UNSAFEfromNumber = $_POST['From'];
$smsStatus = $_POST['SmsStatus']; // e.g received

// check for whether this user has setup
$conn = new mysqli($DBServer, $DBUser, $DBPass, $DBName);

// check for correct connection
if ($conn->connect_error) {
    // send error to user
    die(sendMessage("Internal Error", $UNSAFEfromNumber));
} 

// get safe id
$SAFEUSERNUMBER = $conn->real_escape_string($UNSAFEfromNumber);

// reset the queue
if ($bodyMessage == "AMI reset queue")
{
    $sql = "UPDATE users SET `dead`='1'";
    $result = $conn->query($sql);
    
    if ($result == true)
    {
        sendMessage("Ok boss, done 😎", $UNSAFEfromNumber);
    }else {
        sendMessage("Sorry boss, couldn't do that.", $UNSAFEfromNumber);
    }
    
    
    $conn->close();
    die();
}

// get the details for the required user
$sql = "SELECT * FROM `users` WHERE `phone_number`=$SAFEUSERNUMBER AND `dead`=0";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // there was a result -- it will be the user, just 1 result
    while($row = $result->fetch_assoc()) {
        // the user is here, check what stage
        
        if ($row["has_twitter"] == NULL)
        {
            // they should have replied with their name save this name
            if ((strpos(strtolower($bodyMessage), 'yes') !== FALSE)&&(strpos(strtolower($bodyMessage), 'no') == FALSE))
            {
                // they do have a twitter acount
                $SAFENAME = $conn->real_escape_string($bodyMessage);
                $sql = "UPDATE `users` SET `has_twitter`=1 WHERE `phone_number`='$SAFEUSERNUMBER' AND `dead`=0";

                if ($conn->query($sql) === TRUE) {
                    sendMessage("What's your first name? So I know what to call you.", $UNSAFEfromNumber);
                } else {
                    sendMessage("Internal Error: ".$conn->error, $UNSAFEfromNumber);
                }
                
            }else if ((strpos(strtolower($bodyMessage), 'no') !== FALSE)&&(strpos(strtolower($bodyMessage), 'yes') == FALSE))
            {
                // they dont have a twitter account
                sendMessage("Sorry, you need a twitter account to interact with this piece.\n\nStick around, someone will.", $UNSAFEfromNumber);
            }
            
        }else if ($row["first_name"] == "unknown")
        {   
            // they should have replied with their name save this name
            $SAFENAME = $conn->real_escape_string($bodyMessage);
            $sql = "UPDATE `users` SET `first_name`='$SAFENAME' WHERE `phone_number`='$SAFEUSERNUMBER' AND `dead`=0";
            
            if ($conn->query($sql) === TRUE) {
                sendMessage("Hi ".$SAFENAME.", what's your twitter address?", $UNSAFEfromNumber);
            } else {
                sendMessage("Internal Error: ".$conn->error, $UNSAFEfromNumber);
            }
            
            
        }else if ($row["username"] == "unknown")
        {   
            // they should have replied with their name save this name
            $SAFEUSERNAME = $conn->real_escape_string(str_replace("@", "", $bodyMessage));
            
            $sql = "UPDATE `users` SET `username`='$SAFEUSERNAME', `constructing`='1' WHERE `phone_number`='$SAFEUSERNUMBER' AND `dead`=0";
            
            if ($conn->query($sql) === TRUE) {
                sendMessage("Thanks, I'm just going to set a few things up. I'll text you back in a few minutes.", $UNSAFEfromNumber);
                
                // get the user's name
                $sql = "SELECT first_name FROM `users` WHERE phone_number='$UNSAFEfromNumber' AND `dead`=0";
                $first_name = strtolower($SAFEUSERNAME);
                $result = $conn->query($sql);
                if ($result->num_rows > 0) {
                    // output data of each row
                    while($row = $result->fetch_assoc()) {
                        $first_name = $row["first_name"];
                    }
                }
                
                // procede to set up the user's hierachy and structure
                $output = shell_exec('cd /var/www/api.joemcalister.com/html/ami/ && sh start.sh '.strtolower($SAFEUSERNAME).' '.strtolower($first_name)); // 'cd /var/www/api.joemcalister.com/html/ami/ && sh start.sh '.$SAFEUSERNAME
                
                // check for success
                if ((strpos($output, 'Okay.') !== FALSE)) //(strpos($output, 'Okay.') !== FALSE)
                {
                    // there was an error of sorts -- reset the mysql so it's no longer pending and instead back in username mode
                    $sql = "UPDATE `users` SET `constructing`='0', `queuing`='1' WHERE `phone_number`='$SAFEUSERNUMBER' AND `dead`=0";
                    if ($conn->query($sql) === TRUE) {
                        
                        // get the number of the user in the queue
                        $queue_num = shell_exec('cd /var/www/api.joemcalister.com/html/ami/ && php queue/check/getPosition.php '.$SAFEUSERNUMBER);
                        
                        sendMessage("Okay, everything is set up, currently you are number $queue_num in the queue.\n\nI'll text you a few moments before it's your turn.", $UNSAFEfromNumber);
                    }else {
                        sendMessage("Oh no! There was a unexpected issue with setting you up.", $UNSAFEfromNumber);
                    }
                    
                }else {
                    // there was an error of sorts -- reset the mysql so it's no longer pending and instead back in username mode
                    $sql = "UPDATE `users` SET `constructing`='0', `username`='unknown' WHERE `phone_number`='$SAFEUSERNUMBER' AND `dead`=0";
                    if ($conn->query($sql) === TRUE) {
                        sendMessage("There was an issue with setting up, ".$output."\nType another username to try again.", $UNSAFEfromNumber);
                    }else {
                        sendMessage("There was an issue with setting up, ".$output."\nUnfortuantly you're unable to use this piece today.", $UNSAFEfromNumber);
                    }
                }
                
                
            } else {
                sendMessage("Internal Error: ".$conn->error, $UNSAFEfromNumber);
            }
            
            
        }else {
            sendMessage("I'm unsure what you mean by that.", $UNSAFEfromNumber);
        }
    }

} else {
    // there was no such user, treat them as new, we add a new entry and ask for name
    $sql = "INSERT INTO `users`( `phone_number`, `first_name`, `username`) VALUES ('$SAFEUSERNUMBER','unknown','unknown')";

    if ($conn->query($sql) === TRUE) {
        sendMessage("I am A.M.I.\n\nBefore I introduce myself, do you have public (e.g. not protected) twitter account?\n\nReply yes or no.", $UNSAFEfromNumber);
    } else {
        sendMessage("Internal Error: ".$conn->error, $UNSAFEfromNumber);
    }
}

// close the connection
$conn->close();


function sendMessage($m, $n)
{
    // Your Account SID and Auth Token from twilio.com/console
    $sid = 'REMOVED';  // something else SK15396d3d2d7760a32d26354dd0ebf979 secret 2XFuL9l90U8uOBmluNkFFBCCJrpct6CM
    $token = 'REMOVED';
    $client = new Client($sid, $token);

    // Use the client to do fun stuff like send text messages!
    $client->messages->create(
        // the number you'd like to send the message to
        $n,
        array(
            // A Twilio phone number you purchased at twilio.com/console
            'from' => '',
            // the body of the text message you'd like to send
            'body' => $m
        )
    );
}






?>