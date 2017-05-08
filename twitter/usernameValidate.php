<?php

// check arguments
$screenname = $argv[1];
if (($screenname == null)||(strlen($screenname) == 0))
{
    die("No username provided.");
}

// it's okay
require_once('api/TwitterAPIExchange.php');
require_once('credentials/cred.php');

$url = 'https://api.twitter.com/1.1/statuses/user_timeline.json';
$getfield = "?screen_name=$screenname&count=100&exclude_replies=false";
$requestMethod = 'GET';

$twitter = new TwitterAPIExchange($settings);
$tweets = $twitter->setGetfield($getfield)
    ->buildOauth($url, $requestMethod)
    ->performRequest();

// check for username error
$decoded = json_decode($tweets);

if (!empty($decoded->errors))
{
    // there was an error
    echo "that username doesn't seem to exist.";
    
}else {
    // the user does exist
    
    // create our insight
    if (count($decoded) < 10)
    {
        // there are less than 10 tweets
        echo "you have too few tweets.";
    }else {
        echo "Okay.";
    }
}

?>