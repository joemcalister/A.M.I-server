<?php

// check arguments
$screenname = $argv[1];
$filepath = $argv[2];
if (($screenname == null)||(strlen($screenname) == 0))
{
    die("No username provided.");
}

if (($filepath == null)||(strlen($filepath) == 0))
{
    die("No filepath provided.");
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
    echo "No images were found.";
    
    // save the all tweets text file
    $file = "$filepath/tweetdata.txt";
    file_put_contents($file, json_encode($decoded));
    
}else {
    // the user does have tweets, scan for images
    
    // create our insight
    $mediaURLS = array();
    
    $hasProfile = false;
    foreach ($decoded as $tweet)
    {
        // get entities
        $entities = $tweet->entities;
        
        // get profile picture
        if (!$hasProfile)
        {
            $hasProfile = true;
            $profile_pic = str_replace("_normal", "", $tweet->user->profile_image_url_https);
            $profile_file = "$filepath/profile_pic.jpg";
            file_put_contents($profile_file, file_get_contents($profile_pic));
        }
        
        if (!empty($entities->media))
        {
            // there is media
            foreach($entities->media as $image)
            {
                $package = array("url"=>$image->media_url_https,"id"=>$image->id_str, "full"=>$tweet);
                $mediaURLS[] = $package;
            }
        }
    }
    
    // check if any was found
    if (!empty($mediaURLS))
    {
        // there were some found
        foreach($mediaURLS as $imagePacket)
        {
            $img = $filepath.$imagePacket["id"].".jpg";
            file_put_contents($img, file_get_contents($imagePacket["url"]));
        }
        
        // save the text file
        $file = "$filepath/metadata.txt";
        file_put_contents($file, json_encode($mediaURLS));
        
        // save the all tweets text file
        $file = "$filepath/tweetdata.txt";
        file_put_contents($file, json_encode($decoded));
        
        // echo that it was succesful
        echo "Okay.";
    }else {
        // none was found
        echo "No images were found.";
        
        // save the all tweets text file
        $file = "$filepath/tweetdata.txt";
        file_put_contents($file, json_encode($decoded));
    }
}

?>