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
$getfield = "?id=$screenname&count=1&exclude_replies=false";
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
    echo "Error.";
    
}else {
    // return the url of profile pic
    echo str_replace("_normal", "", $decoded[0]->user->profile_image_url_https); 
}

?>