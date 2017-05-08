#!/bin/bash

# check if username has been passed
if [ -z "$1" ]
  then
    echo "No username was supplied."
    exit 1;
fi

# check if first name has been passed
if [ -z "$2" ]
  then
    echo "No first name was supplied."
    exit 1;
fi

# try and validate the username
valid="$(php twitter/usernameValidate.php $1)"
if [ $valid = "Okay." ]
  then
    echo "Username is valid,"
  else
    echo $valid
    exit 1;
fi

# create datafiles for the username
# rm -r used in case user has already used this piece and a folder exists
# in this instance it is simply overridden
rm -r data/users/$1
mkdir -p data/users/$1/images
mkdir -p data/users/$1/data

# grab neccesary images from the account
PWD="`pwd`"
images="$(php twitter/grabImages.php $1 "$PWD/data/users/$1/images/")"
if [ $images != "Okay." ]
  then
    echo "Saved found images, passing through face detection,"
  else
    echo "NON-FATAL ERROR: User images: $images"
fi

# loop through all files in image directory and create their subfolders
# also pass this through the face capture
for f in "$PWD/data/users/$1/images/"*.jpg
do
    # grab the filename of the images, stripped of extension
    file=$(basename $f)
    filenoext="${file%.*}"
    
    # make the directory for the image and put inside
    mkdir data/users/$1/images/$filenoext
    mkdir data/users/$1/images/$filenoext/faces
    mv data/users/$1/images/$file data/users/$1/images/$filenoext/"original.jpg" 
    
    # get the relative paths for these files
    profilepath=$(dirname "${f}")
    profilepath=$profilepath"/"$filenoext
    profilefilename=$(dirname "${f}")
    profilefilename=$profilefilename"/"$filenoext"/original.jpg"
    
    # pass this through face detection
    detection/face/facedetect $profilepath $profilefilename
done

# TEMPORARY copy the test script file to the user's directory
#cp testscript.txt data/users/$1/data/script.txt

# move the tweetdata file to an obvious place
mv data/users/$1/images/tweetdata.txt data/users/$1/data/tweetdata.txt

# run the script generation
#script="$(python script/main.py $1)"
#if [ $script != "Okay." ]
#  then
#    echo "$script"
#    exit 1;
#  else
#    echo "Generated the script,"
#fi

echo "Attempting to generate script"
python script/main.py $1 $2

# echo that everything went okay
#echo "Okay."