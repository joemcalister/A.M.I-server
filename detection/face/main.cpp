// Basic face detection
// Based on http://codereview.stackexchange.com/questions/28115/opencv-2-4-5-face-detection

#include <iostream>
#include <sys/stat.h>
#include "opencv2/objdetect/objdetect.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

using namespace std;
using namespace cv;

void detect(Mat frame, char* argv[]);

// face cascade classifier
CascadeClassifier face_cascade;
int filenumber;
string filename;

// Function main
int main(int argc, char* argv[])
{
    // check if arguments are there
    if (argc <= 2)
    {
        cout << "Fatal Error: No filepaths specified." << endl;
        return -1;
    }
    
    // load the initial cascade
    if (!face_cascade.load("/var/www/api.joemcalister.com/html/ami/detection/face/haarr.xml")){
        cout << "Error: Couldn't find the Haar file." << endl;
        return -1;
    }

    // load in the image to analyse
    Mat frame = imread(argv[2]);

    // apply the classifier
    if (!frame.empty()){
        detect(frame, argv);
        
    }else{
        cout << "Error: No image submitted." << endl;
    }
    
    return 0;
}

// detect the faces in the image
void detect(Mat frame, char* argv[])
{
    vector<Rect> faces;
    Mat frame_gray;
    Mat crop;
    Mat res;
    Mat gray;
    string text;
    stringstream sstm;

    cvtColor(frame, frame_gray, COLOR_BGR2GRAY);
    equalizeHist(frame_gray, frame_gray);

    // detect the faces in the image
    face_cascade.detectMultiScale(frame_gray, faces, 1.1, 10, 0 | CASCADE_SCALE_IMAGE, Size(30, 30));

    // Set Region of Interest
    Rect roi_b;
    Rect roi_c;

    size_t ic = 0; // ic is index of current element
    int ac = 0; // ac is area of current element

    size_t ib = 0; // ib is index of biggest element
    int ab = 0; // ab is area of biggest element
    
    // loop through all the faces found
    cout << faces.size() << " face(s) were/was found." << endl;
    for (ic = 0; ic < faces.size(); ic++)
    { 
        roi_c.x = faces[ic].x;
        roi_c.y = faces[ic].y;
        roi_c.width = (faces[ic].width);
        roi_c.height = (faces[ic].height);

        ac = roi_c.width * roi_c.height; // Get the area of current element (detected face)

        roi_b.x = faces[ib].x;
        roi_b.y = faces[ib].y;
        roi_b.width = (faces[ib].width);
        roi_b.height = (faces[ib].height);

        ab = roi_b.width * roi_b.height; // Get the area of biggest element, at beginning it is same as "current" element

        if (ac > ab)
        {
            ib = ic;
            roi_b.x = faces[ib].x;
            roi_b.y = faces[ib].y;
            roi_b.width = (faces[ib].width);
            roi_b.height = (faces[ib].height);
        }

        // crop face out of image
        crop = frame(roi_c);
        resize(crop, res, Size(128, 128), 0, 0, INTER_LINEAR); // This will be needed later while saving images
        
        // create a new directory for the face
        ostringstream filepath;
        filepath << argv[1] << "/faces/" << filenumber;
        string filepathstr = filepath.str();
        
        char * filepathcst = new char [filepathstr.length()+1];
        strcpy(filepathcst, filepathstr.c_str());
        
        const int dir_err = mkdir(filepathcst, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
        if (-1 == dir_err)
        {
            printf("Error creating directory!n");
            exit(1);
        }
        
        // Form a filename
        filename = "";
        stringstream ssfn;
        ssfn << argv[1] << "/faces/" << filenumber << "/" << "crop.png";
        filename = ssfn.str();
        filenumber++;
        imwrite(filename, crop);
        
        // positions
        stringstream positions;
        positions << faces[ic].x << "," << faces[ic].y << "," << faces[ic].width << "," << faces[ic].height;
    }
}
