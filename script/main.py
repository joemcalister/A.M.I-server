# -*- coding: utf-8 -*-
import sys
import json
import os
import subprocess
import wave
import contextlib
from stormkit.sentimentAnalysis import *
import RAKE
import operator
from webscrape import *
import httplib
import re
import enchant
import random
import fnmatch


def main():
    # sys.argv
    
    if len(sys.argv) < 2:
        print 'ERROR: No username provided.'
        sys.exit()
    
    # init rake
    rake_object = RAKE.Rake("/var/www/api.joemcalister.com/html/ami/script/stoplist.txt")
    
    # open the stored tweet file, this contains all the users most recent tweets
    f = open("/var/www/api.joemcalister.com/html/ami/data/users/"+sys.argv[1]+"/data/tweetdata.txt","r") 

    # decode the JSON
    tweetPayload = json.load(f)
    
    # close f
    f.close()
    
    # check for existance of tweets
    if (len(tweetPayload) > 0):
        # We are fine, yay -- start the script building process
        print "Beginning the scripting proccess"
       
        # --- TWEET ANALYTICS ---
        
        # lets check for sentiment using stormkit
        sentiment = MultiMoodSentimentAnalysis()
        sentimentArray = []
        
        # itterate through all tweets and check for their sentiment
        index = 0
        negIndex = -1 
        negValue = 0
        posIndex = -1
        posValue = 0
        angryIndex = -1
        angryValue = 0
        sadIndex = -1
        sadValue = 0
        worryIndex = -1
        worryValue = 0
        scareIndex = -1
        scareValue = 0
        d = enchant.Dict("en_UK")
        for tweet in tweetPayload:
            result = sentiment.analyse_text(sanitiseTweet(tweet["text"]))
            
            #print result.decimals
            sentimentArray.append(result)
            
            # we need the most positive and negative things, do it here so its more efficient
            if result.decimals["negative"] > negValue:
                # run a test on the word to see if they're logical before commiting to it
                keywords = rake_object.run(sanitiseTweet(tweet["text"]))
                negValue = result.decimals["negative"]
                negIndex = index
                
            if result.decimals["positive"] > posValue:
                # run a test on the word to see if they're logical before commiting to it
                keywords = rake_object.run(sanitiseTweet(tweet["text"]))
                posValue = result.decimals["positive"]
                posIndex = index
                
            if result.decimals["angry"] > angryValue:
                # run a test on the word to see if they're logical before commiting to it
                keywords = rake_object.run(sanitiseTweet(tweet["text"]))
                angryValue = result.decimals["angry"]
                angryIndex = index
                
            if result.decimals["sad"] > sadValue:
                # run a test on the word to see if they're logical before commiting to it
                keywords = rake_object.run(sanitiseTweet(tweet["text"]))
                sadValue = result.decimals["sad"]
                sadIndex = index
                
            if result.decimals["worried"] > worryValue:
                # run a test on the word to see if they're logical before commiting to it
                keywords = rake_object.run(sanitiseTweet(tweet["text"]))
                worryValue = result.decimals["worried"]
                worryIndex = index
                    
            if result.decimals["scared"] > scareValue:
                # run a test on the word to see if they're logical before commiting to it
                keywords = rake_object.run(sanitiseTweet(tweet["text"]))
                scareValue = result.decimals["scared"]
                scareIndex = index
            
            index += 1
             
        # get keyword for the objects
        negative_keywords = []
        if negIndex != -1:
            negative_keywords = rake_object.run(sanitiseTweet(tweetPayload[negIndex]["text"]))
        
        positive_keywords = []
        if posIndex != -1:
            positive_keywords = rake_object.run(sanitiseTweet(tweetPayload[posIndex]["text"]))
            
        angry_keywords = []
        if angryIndex != -1:
            angry_keywords = rake_object.run(sanitiseTweet(tweetPayload[angryIndex]["text"]))
            
        sad_keywords = []
        if sadIndex != -1:
            sad_keywords = rake_object.run(sanitiseTweet(tweetPayload[sadIndex]["text"]))
            
        worry_keywords = []
        if worryIndex != -1:
            worry_keywords = rake_object.run(sanitiseTweet(tweetPayload[worryIndex]["text"]))
            
        scare_keywords = []
        if scareIndex != -1:
            scare_keywords = rake_object.run(sanitiseTweet(tweetPayload[scareIndex]["text"]))
        
        # get the individual words
        negative_word = tryDodgyWord(negative_keywords)
        positive_word = tryDodgyWord(positive_keywords)
        angry_word = tryDodgyWord(angry_keywords)
        sad_word = tryDodgyWord(sad_keywords)
        worry_word = tryDodgyWord(worry_keywords)
        scare_word = tryDodgyWord(scare_keywords)
        
        # grab the emotions
        emotions = [{"word":positive_word, "emotion":"positive", "image":"", "dead":False}, {"word":negative_word, "emotion":"negative", "image":"", "dead":False}, {"word":angry_word, "emotion":"angry", "image":"", "dead":False}, {"word":sad_word, "emotion":"sad", "image":"", "dead":False}, {"word":worry_word, "emotion":"worry", "image":"", "dead":False}, {"word":scare_word, "emotion":"scared", "image":"", "dead":False}]
        
        # populate the emotions with images
        for emotion in emotions:
            if len(emotion["word"]) > 0:
                # get image url
                imageUrl = getImageForTerm(emotion["word"])

                # set the dict to == the okay url
                if imageUrl is not None:
                    emotion["image"] = imageUrl
                else:
                    print "Error finding viable image"
                    emotion["image"] = returnFakeEmotionImage(emotion["emotion"])
                
            else:
                print "Error finding an image"
                emotion["image"] = returnFakeEmotionImage(emotion["emotion"])
      
        # look for common locations
        locations_mentioned = []
        user_images = []
        mentioned_people = []
        profile_location = None
        for tweet in tweetPayload:
            if "rt:" not in tweet["text"].lower():
                # this is not a retweet   
                if tweet["user"]["location"] is not None and profile_location is None:
                    profile_location = tweet["user"]["location"]
                
                if "user_mentions" in tweet["entities"].keys():
                    for users in tweet["entities"]["user_mentions"]:
                        # check if they exist already
                        
                        # dont allow themseleves to be added
                        if users["screen_name"].lower() != sys.argv[1].lower():
                            found = False
                            for person in mentioned_people:
                                if person["name"] == users["name"]:
                                    person["frequency"] += 1
                                    found = True
                                    break

                            if found is False:
                                mentioned_people.append({"name":users["name"], "id":users["id"], "frequency":1, "body":tweet["text"], "screen_name":users["screen_name"]})
                
                if "media" in tweet["entities"].keys():
                    for images in tweet["entities"]["media"]:
                        user_images.append(images["media_url_https"])
                    
                if tweet["place"] is not None:
                    # there is a specific place
                    full_search_string = tweet["place"]["name"]+", "+tweet["place"]["country"]
                    
                    # check for existing
                    add = True
                    for location in locations_mentioned:
                        if location["location"] == full_search_string:
                            add = False
                            
                    # add the location
                    if add:
                        # check for users mentioned
                        users = tweet["entities"]["user_mentions"]
                        final_users = []
                        for user in users:
                            final_users.append({"name":user["name"],"username":user["screen_name"]})
                        
                        locations_mentioned.append({"location":full_search_string, "users_info":final_users})
             
            
        # get images for the common locations
        for location in locations_mentioned:
            # get image url
            imageUrl = getImageForTerm(location["location"])
            
            # set the dict to == the okay url
            if imageUrl is not None:
                location["url"] = imageUrl
            else:
                location["url"] = ""  
            
        # get an image for the location
        profile_location_images = []
        if len(user_images) is not 0:
            profile_location_images.extend(user_images)
            
        if profile_location is not None:
            # there is a location!
            images = get_related_images(profile_location+" photograph")

            # check for those image links being dead (ocassionally happens)
            okayurl = ""
            for src in images:
                first_pass = src.replace("https://", "")
                second_pass = src.replace("http://", "") # may still be old-school
                parts = second_pass.split("/")
                domain = parts[0]
                path = ""
                for part in parts:
                    if part != domain:
                        path = path+"/"+part

                # get header to see if it's there
                status_code = get_status_code(domain, path)

                if status_code == 200:
                    okayurl = src
                    profile_location_images.append(okayurl)
                    
                    if len(profile_location_images) > 7:
                        break # we want to stop this loop as soon as possible

            # set the dict to == the okay url
            if okayurl != "":
                pass
            else:
                print "Error finding viable image"
                emotion["image"] = None
        
        # --- TWEET ANALYTICS ---
        
        
        
        
        # --- SCRIPT BUILDING ---
        
        # create script
        payload = {"success":1, "script":[]}

        # create ongoingtime
        ongoingtime = 5.5
        
        # initiate it with the default start
        defaultstart = {"order":1, 
                           "text":"",
                           "voice":"",
                           "duration":ongoingtime,
                           "isolate":"none",
                           "preset":"",
                           "objects":[{"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"}
                                     ],
                       "is_video":"false"}
        
        # add the default start
        payload["script"].append(defaultstart)

        
        # determine a random clip
        clips1 = ["gaga-1.mp4", "gaga-2.mp4", "gaga-3.mp4", "gaga-4.mp4"]
        
        # create ongoingtime
        ongoingtime += 1.5
        
        # initiate it with the default start
        defaultstart2 = {"order":1, 
                           "text":"",
                           "voice":"",
                           "duration":ongoingtime,
                           "isolate":"",
                           "preset":"",
                           "objects":[{"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"}],
                       "is_video":"true",
                       "video_path":"/Users/joe/Desktop/ami_buffer_files/protected/snippets/"+random.choice(clips1)}
        
        # add the default start
        payload["script"].append(defaultstart2)
        
        
        # create ongoingtime
        ongoingtime += 0.8
        
        # initiate it with the default start
        defaultstart3 = {"order":1, 
                           "text":"",
                           "voice":"",
                           "duration":ongoingtime,
                           "isolate":"none",
                           "preset":"",
                           "objects":[{"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"}],
                       "is_video":"false",
                       "video_path":""}
        
        # add the default start
        payload["script"].append(defaultstart3)
        
        
        # create ongoingtime
        ongoingtime += 1.5
        
        # determine a random clip
        clips2 = ["trump-1.mp4", "kadyrov-1.mp4", "farage-1.mp4", "police-1.mp4", "nkorea-1.mp4", "may-1.mp4"]
        
        # initiate it with the default start
        defaultstart4 = {"order":1, 
                           "text":"",
                           "voice":"",
                           "duration":ongoingtime,
                           "isolate":"",
                           "preset":"",
                           "objects":[{"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"}],
                       "is_video":"true",
                       "video_path":"/Users/joe/Desktop/ami_buffer_files/protected/snippets/"+random.choice(clips2)}
        
        # add the default start
        payload["script"].append(defaultstart4)
        
        
        # create ongoingtime
        ongoingtime += 1.0
        
        # initiate it with the default start
        defaultstart5 = {"order":1, 
                           "text":"",
                           "voice":"",
                           "duration":ongoingtime,
                           "isolate":"none",
                           "preset":"",
                           "objects":[{"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                          {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"}],
                       "is_video":"false",
                       "video_path":""}
        
        # add the default start
        payload["script"].append(defaultstart5)
        
        
        
        # create the script lines
        for i in range(2,10):
            
            # create the text
            text = "Testing 123..."
            
            # get the correct line for the script
            scriptline = {}
            if i == 2:
                text = "Hello "+sys.argv[2]+", Don't be scared, I'm not real, I am Amy."
            
                # generate the speech elements
                scriptElements = genSpeech(text)
            
                # itterate ongoing time
                ongoingtime += float(scriptElements[1])

                # form the actual script entry
                scriptline = {"order":i, 
                               "text":text,
                               "voice":scriptElements[0],
                               "duration":ongoingtime,
                               "isolate":"",
                               "preset":"",
                               "objects":[{"resource":"https://api.joemcalister.com/ami/data/users/"+sys.argv[1]+"/images/profile_pic/original.jpg", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"https://api.joemcalister.com/ami/data/users/"+sys.argv[1]+"/images/profile_pic/original.jpg", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"https://api.joemcalister.com/ami/data/users/"+sys.argv[1]+"/images/profile_pic/original.jpg", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"https://api.joemcalister.com/ami/data/users/"+sys.argv[1]+"/images/profile_pic/original.jpg", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"https://api.joemcalister.com/ami/data/users/"+sys.argv[1]+"/images/profile_pic/original.jpg", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"https://api.joemcalister.com/ami/data/users/"+sys.argv[1]+"/images/profile_pic/original.jpg", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"https://api.joemcalister.com/ami/data/users/"+sys.argv[1]+"/images/profile_pic/original.jpg", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"https://api.joemcalister.com/ami/data/users/"+sys.argv[1]+"/images/profile_pic/original.jpg", "delay":0, "spotlight":"false", "is_video":"false"}
                                         ],
                             "is_video":"false"}
                
                # we add this line to the script
                payload["script"].append(scriptline)
                
            elif i == 3:
                text = "I am not human. Instead something different. A subconscious; a collective of memories and thoughts that are often hard to explain. I was built to help understand these feelings; by an artist keen to justify their own."
            
                # generate the speech elements
                scriptElements = genSpeech(text)
            
                # itterate ongoing time
                ongoingtime += float(scriptElements[1])

                # form the actual script entry
                scriptline = {"order":i, 
                               "text":text,
                               "voice":scriptElements[0],
                               "duration":ongoingtime,
                               "isolate":"4",
                               "preset":"",
                               "objects":[{"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"}
                                         ],
                             "is_video":"true",
                             "video_path":"/Users/joe/Desktop/ami_buffer_files/protected/snippets/farage-2.mp4"}
                
                # we add this line to the script
                payload["script"].append(scriptline)
                
            elif i == 4:
                
                # add explanation
                text = "Small and insignificant events that are easily forgettable can often play a large role in our emotions. Social media provides a way of looking back and reflecting on the past, studying what makes us feel this way. "

                # generate the speech elements
                scriptElements = genSpeech(text)

                # itterate ongoing time
                ongoingtime += float(scriptElements[1])

                # form the actual script entry
                scriptline = {"order":i, 
                               "text":text,
                               "voice":scriptElements[0],
                               "duration":ongoingtime,
                               "isolate":"",
                               "preset":"",
                               "objects":[{"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"}
                                         ],
                              "is_video":"true",
                              "video_path":"/Users/joe/Desktop/ami_buffer_files/protected/snippets/static.mp4"
                             }

                # we add this line to the script
                payload["script"].append(scriptline)
                
                
                
                # specific emotions here
                last_random_index = ""
                random_index = ""
                for emot in emotions:
                    # check the emotion
                    if emot["word"] is not "":
                        
                        text = ""
                        if emot["emotion"] is "positive":
                            text = "Whether it's "+emot["word"]+"; something that you're positive about"
                        elif emot["emotion"] is "negative":
                            text = emot["word"]+"; which makes you negative."
                        elif emot["emotion"] is "angry":
                            text = "Times "+emot["word"]+" pushes you to your limits;"
                        elif emot["emotion"] is "sad":
                            text = "and consequently the times "+emot["word"]+" makes you sad."
                        elif emot["emotion"] is "worry":
                            text = "And its when "+emotion["word"]+" makes you worried"
                        elif emot["emotion"] is "scared":
                            text = "or when "+emotion["word"]+" makes you petrified you consider everthing from a new perspective."
                        else:
                            text = emot["word"]+" makes you feel "+emot["emotion"]

                        # generate the speech elements
                        scriptElements = genSpeech(text)

                        # itterate ongoing time
                        ongoingtime += float(scriptElements[1])

                        # random index
                        ind = ["0","1","2","3","5","6"]
                        
                        # create the brain dictionary
                        start_delay = 0;
                        brains_emotions = []
                        
                        while last_random_index == random_index:
                            random_index = random.choice(ind)
                            
                        last_random_index = random_index
                        
                        for i in range(0,7):
                            if i == int(random_index):
                                 brains_emotions.append({"resource":emot["image"], "delay":0, "spotlight":"false", "is_video":"false"})
                            else:
                                 brains_emotions.append({"resource":"", "delay":0, "spotlight":"false", "is_video":"false"})

                        # form the actual script entry
                        scriptline = {"order":i, 
                                       "text":text,
                                       "voice":scriptElements[0],
                                       "duration":ongoingtime,
                                       "isolate":random_index,
                                       "preset":"",
                                       "objects":brains_emotions,
                                       "is_video":"false",
                                       "video_path":""
                                     }

                        # we add this line to the script
                        payload["script"].append(scriptline)
                
            elif i == 5:
                # how specific should we be
                spec = "Whether is the time spent at home with loved ones."
                
                # only add this block if they have a location
                if profile_location is not None:
                    spec = "Whether it's your time spent in "+profile_location.split(',')[0]+""
                
                    # create list of people
                    people = []
                    for location in locations_mentioned:
                        if location["users_info"] is not None:
                            for info in location["users_info"]:
                                people.append(info["name"])
                             
                    # add this on to the sentance
                    if len(people) is not 0:
                        spec = spec+"; with "
                        if len(people) == 2:
                            spec = spec+people[0]+" and "+people[1]+"."
                        elif len(people) == 1:
                            spec = spec+people[0]+"."
                        else:
                            p_str_list = ""
                            for p in people:
                                if p is people[0]:
                                    p_str_list = p_str_list+p
                                elif p is not people[-1]:
                                    p_str_list = p_str_list+", "+p
                                else:
                                    p_str_list = p_str_list+" and "+p
                            spec = spec+p_str_list
                        
                    # main body text
                    text = "Locations can form one of the most prevalent parts of an emotion. "+spec+". It can often provide moments of clarity in even the hardest times"

                    # generate the speech elements
                    scriptElements = genSpeech(text)

                    # itterate ongoing time
                    ongoingtime += float(scriptElements[1])

                    # populate all brains with image
                    objects = []
                    for j in range(0,7):
                        if len(profile_location_images) > j and j is not 4:
                            objects.append({"resource":profile_location_images[j], "delay":0, "spotlight":"false", "is_video":"false"})
                        else:
                            objects.append({"resource":"", "delay":0, "spotlight":"false", "is_video":"false"})

                    # form the actual script entry
                    scriptline = {"order":i, 
                                   "text":text,
                                   "voice":scriptElements[0],
                                   "duration":ongoingtime,
                                   "isolate":"",
                                   "preset":"",
                                   "objects":objects
                                 }

                    # we add this line to the script
                    payload["script"].append(scriptline)
                    
                
            elif i == 6:
                text = "These are the memories we cling on to; and rightly so. They provide us with hope and determination that we can get through whatever, no matter what."
            
                # generate the speech elements
                scriptElements = genSpeech(text)
            
                # itterate ongoing time
                ongoingtime += float(scriptElements[1])

                # form the actual script entry
                scriptline = {"order":i, 
                               "text":text,
                               "voice":scriptElements[0],
                               "duration":ongoingtime,
                               "isolate":"4",
                               "preset":"",
                               "objects":[{"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"}
                                         ],
                             "is_video":"false"}
                
                # we add this line to the script
                payload["script"].append(scriptline)
                
            elif i == 7:
                text = "The people that surround us can often have a significant effect on our day to day life. Either adding to it signifciantly, reminding yourself of positive memories or perhaps lesser times."
                    
                face_dir_matches = []
                for root, dirnames, filenames in os.walk('/var/www/api.joemcalister.com/html/ami/data/users/'+sys.argv[1]+'/images/'):
                    for dirname in fnmatch.filter(dirnames, '*'):
                        face_dir_matches.append(os.path.join(root, dirname))
                
                faces_pos_dir = []
                for directories in face_dir_matches:
                    if directories[-5:] == "faces":
                        for root, dirnames, filenames in os.walk(directories):
                            for dirname in fnmatch.filter(dirnames, '*'):
                                faces_pos_dir.append(os.path.join(root, dirname))
                                
                # url-ize these directories
                face_urls = []
                for finals in faces_pos_dir:
                    # turn these to urls
                    url = "https://api.joemcalister.com/ami/"+finals[39:]+"/crop.png"
                    face_urls.append(url)
            
                # generate the speech elements
                scriptElements = genSpeech(text)
            
                # itterate ongoing time
                ongoingtime += float(scriptElements[1])

                # create objects for the faces -- reuse if we run out
                obj = [] 
                recount = 0
                for j in range(0,7):
                    if len(face_urls) > j and j is not 4:
                        obj.append({"resource":face_urls[j], "delay":0, "spotlight":"false", "is_video":"false"})
                    elif j is 4:
                        obj.append({"resource":"", "delay":0, "spotlight":"false", "is_video":"false"})
                    elif len(face_urls) > 0:
                        obj.append({"resource":face_urls[recount], "delay":0, "spotlight":"false", "is_video":"false"})
                        if recount < len(face_urls)-1:
                            recount += 1
                        else:
                            recount = 0
                    else:
                        obj.append({"resource":"", "delay":0, "spotlight":"false", "is_video":"false"})
                
                # form the actual script entry
                scriptline = {"order":i, 
                               "text":text,
                               "voice":scriptElements[0],
                               "duration":ongoingtime,
                               "isolate":"",
                               "preset":"",
                               "objects":obj,
                             "is_video":"false"}
                
                # we add this line to the script
                payload["script"].append(scriptline)
                
            
            elif i == 8:
                text = "Even the most seemingly insignificant conversations can often form connections and ideas, later influencing your life;"
            
                # generate the speech elements
                scriptElements = genSpeech(text)
            
                # itterate ongoing time
                ongoingtime += float(scriptElements[1])

                # form the actual script entry
                scriptline = {"order":i, 
                               "text":text,
                               "voice":scriptElements[0],
                               "duration":ongoingtime,
                               "isolate":"4",
                               "preset":"",
                               "objects":[{"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"}
                                         ],
                             "is_video":"false"}
                
                # we add this line to the script
                payload["script"].append(scriptline)
                
                # create the info for two additional references
                if len(mentioned_people) >= 2:
                    
                    # determine who is the most popular two -- may defualt to most recent 2
                    first = mentioned_people[0];
                    second = mentioned_people[1];
                    for p in mentioned_people:
                        if p["frequency"] > first["frequency"]:
                            first = p
                        elif p["frequency"] > second["frequency"]:
                            second = p
                            
                    # get the keywords for these discussions 
                    first_keywords = rake_object.run(first["body"])
                    second_keywords = rake_object.run(second["body"])
                    
                    # get the images for the users
                    first_image = subprocess.check_output(["php", "/var/www/api.joemcalister.com/html/ami/twitter/getProfilePic.php", first["screen_name"]])
                    second_image = subprocess.check_output(["php", "/var/www/api.joemcalister.com/html/ami/twitter/getProfilePic.php", second["screen_name"]])
                    
                    # fix a potential crash if index doesnt contain word
                    first_word = tryDodgyWord(first_keywords[0])
                    second_word = tryDodgyWord(second_keywords[1])
                    
                    # create the strings for both users
                    if first_word == "" and second_word == "":
                        text = "Perhaps talking to "+first["name"]+"."
                    elif first_word == "":
                        text = "Perhaps talking to "+first["name"]+" about "+second_word
                    elif second_word == "":
                        text = "Perhaps talking to "+first["name"]+" about "+first_word
                    else:
                        text = "Perhaps talking to "+first["name"]+" about "+first_keywords[0][0]+" and "+first_keywords[1][0]+","

                    # generate the speech elements
                    scriptElements = genSpeech(text)

                    # itterate ongoing time
                    ongoingtime += float(scriptElements[1])

                    # generate the random objects array
                    sel = [0,1,2,3,5,6,7]
                    rand_sel = random.choice(sel)
                    obj = []
                    
                    for i in range(0,7):
                        if i == rand_sel:
                            obj.append({"resource":first_image, "delay":0, "spotlight":"false", "is_video":"false"})
                        else:
                            obj.append({"resource":"", "delay":0, "spotlight":"false", "is_video":"false"})
                    
                    # form the actual script entry
                    scriptline = {"order":i, 
                                   "text":text,
                                   "voice":scriptElements[0],
                                   "duration":ongoingtime,
                                   "isolate":str(rand_sel),
                                   "preset":"",
                                   "objects":obj,
                                 "is_video":"false"}

                    # we add this line to the script
                    payload["script"].append(scriptline)
                    
                    
                    # create the strings for both users
                    text = "or "+second["name"]+" about "+second_keywords[0][0]+" and "+second_keywords[1][0]+"."
            
                    # generate the speech elements
                    scriptElements = genSpeech(text)

                    # itterate ongoing time
                    ongoingtime += float(scriptElements[1])

                    # rand order
                    sel = [0,1,2,3,5,6,7]
                    rand_sel = random.choice(sel)
                    obj = []
                    
                    for i in range(0,7):
                        if i == rand_sel:
                            obj.append({"resource":second_image, "delay":0, "spotlight":"false", "is_video":"false"})
                        else:
                            obj.append({"resource":"", "delay":0, "spotlight":"false", "is_video":"false"})
                            
                    # form the actual script entry
                    scriptline = {"order":i, 
                                   "text":text,
                                   "voice":scriptElements[0],
                                   "duration":ongoingtime,
                                   "isolate":str(rand_sel),
                                   "preset":"",
                                   "objects":obj,
                                 "is_video":"false"}

                    # we add this line to the script
                    payload["script"].append(scriptline)

                
            elif i == 9:
                text = "It's important to realise that every day is never an indication of what is to come. Life is spontanious, random and often quite unexpected. It can bring us happiness and sadness in such small time frames. Strive for those brief moments, enjoy those memories. For I am merely another memory interupted."
            
                # generate the speech elements
                scriptElements = genSpeech(text)
            
                # itterate ongoing time
                ongoingtime += float(scriptElements[1])

                # form the actual script entry
                scriptline = {"order":i, 
                               "text":text,
                               "voice":scriptElements[0],
                               "duration":ongoingtime,
                               "isolate":"4",
                               "preset":"",
                               "objects":[{"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"},
                                      {"resource":"", "delay":0, "spotlight":"false", "is_video":"false"}
                                         ],
                             "is_video":"false"}
                
                # we add this line to the script
                payload["script"].append(scriptline)
 
        
        # write to a file
        w = open("/var/www/api.joemcalister.com/html/ami/data/users/"+sys.argv[1]+"/data/script.txt", "w") 
        w.write(json.dumps(payload))
        w.close()
        
        # --- SCRIPT BUILDING ---
        
        # We are okay and everything has gone well
        print "Ready."
        
        
        #print json.dumps(payload)
        
    else:
        # there are apparenyly no tweets, trigger an error for this
        print 'ERROR: No tweets were found.'
        sys.exit()

def returnFakeEmotionImage(emotion):
    return "https://api.joemcalister.com/ami/prototyping_materials/vague.jpg"
    
    #le = emotion.lower()
    #print "emotion ="+emotion
    #if le == "positive":
    #    return "http://www.pageresource.com/wallpapers/wallpaper/wild-cats-apple-mac-comic-pet-very-happy-cat_467784.jpg"
    #elif le == "negative":
    #    return "http://www.animals-photos.net/wp-content/uploads/2011/06/Cute-or-Sad-.jpg"
    #elif le == "angry":
    #    return "http://memeshappen.com/media/created/Really---meme-52404.jpg"
    #elif le == "sad":
    #    return "http://aspirekc.com/images/86c057f4e31c_13242/unhappy.jpg"
    #elif le == "worry":
    #    return "http://4.bp.blogspot.com/-gJEtKRM42nI/TinfhF_0RgI/AAAAAAAAARE/ju7_z2ggTXo/s1600/Worried.jpg"
    #elif le == "scared":
    #    return "http://www.brick-yard.co.uk/forum/uploads/5328/SCARED.jpg"
    #else:
    #    return "https://mrmodd.it/wp/wp-content/uploads/Kernel_Panic_Mac.gif"
        

def tryDodgyWord(keywords):
    word = ""
    try:
        for worddict in keywords:
            if word == "" and "@" not in worddict[0]:
                word = worddict[0]
    except:
        word = ""
    return word
      
    
def sanitiseTweet(tweet):
    # remove any urls from string
    tweet = re.sub(r"http\S+", "", tweet)
    
    # remove RT: Username
    between = find_between(tweet, "RT @", ":")
    full_phrase = "RT @"+between+": "
    tweet = tweet.replace(full_phrase, "")

    # remove any usernames
    between_username = find_between(tweet, "@", " ")
    full_phrase_username = "@"+between_username+" "
    tweet = tweet.replace(full_phrase_username, "")
    
    return tweet

# below: http://stackoverflow.com/questions/1140661/what-s-the-best-way-to-get-an-http-response-code-from-a-url
def get_status_code(host, path="/"):
    try:
        conn = httplib.HTTPConnection(host)
        conn.request("HEAD", path)
        return conn.getresponse().status
    except StandardError:
        return None
    
def getImageForTerm(term):
    # we need to get an image for the locations
    images = get_related_images(term)

    # check for those image links being dead (ocassionally happens)
    okayurl = ""
    for src in images:
        first_pass = src.replace("https://", "")
        second_pass = src.replace("http://", "") # may still be old-school
        parts = second_pass.split("/")
        domain = parts[0]
        path = ""
        for part in parts:
            if part != domain:
                path = path+"/"+part

        # get header to see if it's there
        status_code = get_status_code(domain, path)

        if status_code == 200:
            okayurl = src
            break # we want to stop this loop as soon as possible

    # return a okayurl if not ''
    if okayurl != "":
        return okayurl
    else:
        return None
    
def genSpeech(text):
    # generate speech file
    speechfile = subprocess.check_output(['sh', '/var/www/api.joemcalister.com/html/ami/speech/cerevoice/generate.sh', '"'+text+'"'])

    # check for trailing new line
    if speechfile.endswith('\n'):
        speechfile = speechfile[:-1]

    # get the filename for the next part
    rawfilename = speechfile.replace("https://api.joemcalister.com/ami/speech/cerevoice/outputs/server_render/", "")

    # get the length of the audio file
    fname = '/var/www/api.joemcalister.com/html/ami/speech/cerevoice/outputs/server_render/'+rawfilename

    # calculate the duration of the sound
    duration = 0
    duration = subprocess.check_output(['sh', '/var/www/api.joemcalister.com/html/ami/script/file_duration.sh', fname])

    # check for trailing new line
    if duration.endswith('\n'):
        duration = duration[:-1]
        
    return [speechfile, duration]
    
main()