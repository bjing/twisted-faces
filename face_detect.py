#!/usr/bin/python

# face_detect.py

# Face Detection using OpenCV. Based on sample code from:
# http://python.pastebin.com/m76db1d6b

# @author: bjing

# Usage: python face_detect.py <image_file>
# Usage: convert marty_mcguire.jpg -stroke red -fill none -draw "rectangle 50,36 115,101" output.jpg

import sys 
import os
import cv
#from opencv.cv import *
#from opencv.highgui import *

def detectObjects(image):
    """Converts an image to grayscale and prints the locations of any 
    faces found"""
    grayscale = cv.CreateImage(cv.GetSize(image), 8, 1)
    cv.CvtColor(image, grayscale, cv.CV_BGR2GRAY)

    # Deprecated v1 code???
    storage = cv.CreateMemStorage(0)
    #cv.ClearMemStorage(storage)
    cv.EqualizeHist(grayscale, grayscale)
    cascade = cv.Load(
            '/home/brian/code/twisted-faces/haarcascade_frontalface_default.xml')
    faces = cv.HaarDetectObjects(grayscale, cascade, storage, 1.2, 2,
        cv.CV_HAAR_DO_CANNY_PRUNING)

#    if faces:
    coords = []
    if faces.total > 0:
        for f in faces:
            #print("[(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
            coords.append({'start':{'x':f.x, 'y':f.y}, 'end':{'x':f.x+f.width, 'y':f.y+f.height}})
    return coords

def draw_face(image_file, coords, output_dir):
    """
    Highlight faces in an image

    Call convert marty_mcguire.jpg -stroke red -fill none -draw "rectangle 50,36 115,101" output.jpg 
    """
    if not os.path.exists(output_dir):
        print 'Output directory %s does not exist, creating it' % output_dir
        os.mkdir(output_dir)

    # Get output name
    image_filename = os.path.basename(image_file)
    output_dir = output_dir.rstrip('/')
    output_filename = output_dir + '/' + 'output-' + image_filename

    from subprocess import Popen
    # Draw faces
    if len(coords) == 0:
        tag_unrecognised(image_file, output_dir)
        return
    else:
        print 'Drawing faces for image "%s", output file: %s' % (image_file, output_filename)
    for coord in coords:
        # Draw face
        cmd = 'convert %s -stroke red -fill none -draw "rectangle %s,%s %s,%s" %s' % \
              (image_file, coord['start']['x'], coord['start']['y'],
              coord['end']['x'], coord['end']['y'], output_filename)
        p = Popen(cmd, shell=True)
        p.wait()

        # If there are multiple faces to draw, draw upon the last output
        image_file = output_filename
        #print coord['coord']['start'] + '-->' + coord['coord']['end']
    
def check_image_validity(f):
    """
    Check whether a given file is a valid image file
    """
    if os.path.isdir(f):
        print '%s is a directory, skipping' % f
        return False

    if f.endswith('jpg') or f.endswith('png') or f.endswith('jpeg'):
        return True
    else:
        print '%s is not a valid image file' % f
        return False

def get_output_dir(input_path, output_path):
    """
    Get output directory from user provided output 
    """
    # If output path is not provided by user, use input path
    if output_path == None:
        #print 'Output path was not specified by user, using input path'
        path = input_path
    else:
        path = output_path
    path = os.path.abspath(path)

    # Get output path
    if os.path.isfile(path):
        output_dir = os.path.dirname(path)
    else:
        output_dir = path
    if not output_dir.endswith('/'):
        output_dir += '/'
    output_dir += 'output/'

    #print '%s, type: %s' % (output_dir, type(output_dir))

    return output_dir

def get_image_files(mode, input_dir):
    """
    Get image or list of images
    """
    image_files = []
    if mode == 'batch':
        if not os.path.isdir(input_dir) or os.path.isfile(input_dir):
            print 'Source path invalid, exiting.'
            sys.exit(1)
        for f in os.listdir(input_dir):
            f = f.lower()
            if check_image_validity(input_dir.rstrip('/') + '/' + f):
                image_files.append(input_dir + '/' + f)
    elif mode == 'single':
        if not os.path.isfile(input_dir):
            print 'Source image file is not valid'
            sys.exit(1)
        else:
            if check_image_validity(input_dir):
                image_files.append(input_dir)
    else:
        print 'Invalid mode specified, please use either "single" or "batch"'
        sys.exit(1)

    return image_files

def tag_unrecognised(image_file, output_dir):
    """
    Tag photo as unrecognised
    """
    print 'Cannot detect faces in the image, tagging the file as unrecognised\n'
    # Send image to the output folder
    import shutil
    filename = os.path.basename(image_file)
    output_filename = output_dir.rstrip('/') + '/' + 'unrecognised-' + filename
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    shutil.copy(image_file, output_filename)

def process_images(image_files, draw, input_path, output_path):
    """
    Process images, draw faces if required.
    """
    print('Number of images to be processed: %s' % len(image_files))
    for image_file in image_files:
        print 'Processing image %s' % image_file

        # Process image
        image = cv.LoadImage(image_file)
        face_coords = detectObjects(image)
        #processed_image = None

        # Highlight faces in images if reqired
        output_dir = get_output_dir(input_path, output_path)
        if draw:
            draw_face(image_file, face_coords, output_dir)
            print '\n'
        else:
            if len(face_coords) == 0:
                tag_unrecognised(image_file, output_dir)
            else:
                print 'Face coords: %s\n' % face_coords

def main():
    
    from optparse import OptionParser
    usage = "Usage: %prog [options]" 
    parser = OptionParser(usage=usage)
    # Single or batch image processing mode
    parser.add_option("-m", "--mode", dest="mode",
            help="Single or batch processing mode")
    # Source image path
    parser.add_option("-s", "--source", dest="source",
            help="Path containing source image(s)")
    # Destination image path
    parser.add_option("-o", "--output", dest="output",
            help="Path containing output image(s)")
    # Highligh/Draw faces in images
    parser.add_option("-d", "--draw-faces",
            action="store_true", dest="draw", default=False,
            help="Highligh/Draw faces in images")
    (options, args) = parser.parse_args()

    # Check command line options
    if options.source == None:
        print "Source directory/file not specified"
        sys.exit(1)
    if options.mode == None:
        print "Mode unknown. Please specified either 'single' or 'batch' mode"
        sys.exit(1)

    # Get a list of image files from user-provided input directory
    image_files = get_image_files(options.mode, options.source)

    # Process images
    process_images(image_files, options.draw, options.source, options.output)
    
    
if __name__ == "__main__":
    main()
