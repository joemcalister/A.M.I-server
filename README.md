![Image of A.M.I](https://joemcalister.com/img/final/articles/ami/ami-hero-2-lower.jpg)

# A.M.I Server-side
This is the backend of an art piece titled A.M.I. More information on the piece can be found [here](https://joemcalister.com/ami). Predominantly this was used to create scripts for the piece, interact with the user via text message and perform textual analysis on the user's twitter account in order to provide information to later use in the piece.

## Basic structure
* "data/users/" folders are created for each user by the shell script start.sh, these are used to store image data, the finalised script and the raw metadata from twitter.
* "detection/face" contains the face detection c++ file and harr.xml. This is used to extract faces from images from the user and subsequently put them in the correct folders.
* "queue" this is the queuing system that allows multiple people to line up to use the app, also contains the view queue page.
* "speech/cerevoice" where speech is generated using the SDK from cereproc, this is not included for licensing reasons.
* "texting" the php system that provides a webhook for twilio allowing the user to text to interact with A.M.I
* "twitter" simple php system to get information about the user using the twitter api.
* "file.txt" used for calibration and testing within the mapping system.
* "start.sh" the core file, this file is called by the texting php system to start the creation of the payload for the user, takes two arguments, twitter username and first name.
* "testscript2.txt" a test script pre-generated and used for demo purposes.

### Sidenote
Why are there so few commits? Embarrassingly I exposed two crucial files during a commit many months ago, these credentials are unable to be changed so therefore I had to restart the git repo without them. The old repos are available to be seen on request.
