import os
import shutil

import cv2

TMP_DIR = 'tmp'

def make_frames(video, dir_name):
    vidcap = cv2.VideoCapture(video)
    success, image = vidcap.read()
    count = 0
    success = True
    while success:
        cv2.imwrite("{}/{}.jpg".format(dir_name, count), image) # save frame as JPEG file
        success,image = vidcap.read()
        print('Read a new frame: ', success)
        count += 1

def cleanup(dir_name):
    shutil.rmtree(dir_name)

def process_video(video):
    # tmp dir for all model images
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

    # tmp dir for this specific model
    dir_name = '{}/{}/{}'.format(os.path.dirname(os.path.abspath(__file__)),
                                 TMP_DIR,
                                 video.filename.split('.')[0])
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    else:
        raise Error('the folder \'{}\' in tmp/ already exists!'.format(dir_name))

    video.save('{}/{}'.format(dir_name, video.filename))

    make_frames(video.filename, dir_name)

    # TODO: actual processing stuff here?

    cleanup(dir_name)

