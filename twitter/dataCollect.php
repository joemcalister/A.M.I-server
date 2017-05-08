<?php

// check arguments
$screenname = $argv[1];
if ($screenname == null)
{
    die("You need to provide a valid screename");
}

// it's okay
require_once('api/TwitterAPIExchange.php');
require_once('credentials/cred.php');
require_once('phpInsight/autoload.php');
require_once('RAKE-PHP/rake.php');

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
    echo json_encode(array("success"=>0, "error_message"=>$decoded->errors[0]->message));
    
}else {
    // the user does exist
    
    // create our insight
    $sentiment = new \PHPInsight\Sentiment();
    $rake = new Rake('RAKE-PHP/stoplist_smart.txt');
    
    $tweets = array();
    foreach ($decoded as $tweet)
    {
        $thistweet = array("text"=>$tweet->text, "sentiment"=>array("scores"=>$sentiment->score($tweet->text),"class"=>$sentiment->categorise($tweet->text)), "keywords"=>$rake->extract($tweet->text));
        $tweets[] = $thistweet;
    }
    
    echo json_encode(array("success"=>1, "payload"=>$tweets));
}


?>