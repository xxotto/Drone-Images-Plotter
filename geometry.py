import numpy as np
import cv2
import math as m
import glob
import pandas as pd
import os


def computeUnRotMatrix(yaw, pitch, roll,):
    '''
    See http://planning.cs.uiuc.edu/node102.html. Undoes the rotation of the craft relative to the world frame.
    :param pose: A 1x6 NumPy ndArray containing pose information in [X,Y,Z,Y,P,R] format
    :return: A 3x3 rotation matrix that removes perspective distortion from the image to which it is applied.
    '''
    
    a = yaw*np.pi/180 #alpha
    b = pitch*np.pi/180 #beta
    g = roll*np.pi/180 #gamma
    #Compute R matrix according to source.
    Rz = np.array(([m.cos(a), -1*m.sin(a),    0],
                   [m.sin(a),    m.cos(a),    0],
                   [       0,           0,     1]))

    Ry = np.array(([ m.cos(b),           0,     m.sin(b)],
                   [        0,           1,            0],
                   [-1*m.sin(b),           0,     m.cos(b)]))

    Rx = np.array(([        1,           0,            0],
                   [        0,    m.cos(g),  -1*m.sin(g)],
                   [        0,    m.sin(g),     m.cos(g)]))
    Ryx = np.dot(Rx,Ry)
    R = np.dot(Rz,Ryx) #Care to perform rotations in roll, pitch, yaw order.
    R[0,2] = 0
    R[1,2] = 0
    R[2,2] = 1
    Rtrans = R.transpose()
    InvR = np.linalg.inv(Rtrans)
    #Return inverse of R matrix so that when applied, the transformation undoes R.
    return InvR


def warpPerspectiveWithPadding(image, transformation):
    '''
    When we warp an image, its corners may be outside of the bounds of the original image. This function creates a new image that ensures this won't happen.
    :param image: ndArray image
    :param transformation: 3x3 ndArray representing perspective trransformation
    :param kp: keypoints associated with image
    :return: transformed image
    '''

    height = image.shape[0]
    width = image.shape[1]
    corners = np.float32([[0,0], [0,height], [width,height], [width,0]]).reshape(-1,1,2) #original corner locations

    warpedCorners = cv2.perspectiveTransform(corners, transformation) #warped corner locations
    [xMin, yMin] = np.int32(warpedCorners.min(axis=0).ravel() - 0.5) #new dimensions
    [xMax, yMax] = np.int32(warpedCorners.max(axis=0).ravel() + 0.5)
    translation = np.array(([1,0,-1*xMin],[0,1,-1*yMin],[0,0,1])) #must translate image so that all of it is visible
    fullTransformation = np.dot(translation, transformation) #compose warp and translation in correct order
    result = cv2.warpPerspective(image, fullTransformation, (xMax-xMin, yMax-yMin))
    return result



def transparency(image):

    width = int(image.shape[1] / 10)
    height = int(image.shape[0] / 10)
    dsize = (width, height)
    img = cv2.resize(image, dsize)

    alpha = np.sum(img, axis=-1) > 0
    alpha = np.uint8(alpha * 255)
    res = np.dstack((img, alpha))

    return res
    



if __name__ == '__main__':

    dataset = '5vuelo'

    # LOAD DATA
    im_paths = sorted(glob.glob('/home/xxotto/Pictures/dataset-mosaicos/' + dataset + '/*.JPG'))
    files_directory = '/home/xxotto/Pictures/dataset-mosaicos/' + dataset + '/'
    df = pd.read_csv(dataset+ '/images_info.csv', index_col=0)

    # CREATE DEST PATH
    destination_directory = files_directory.split("/")[-2]
    if not os.path.exists(destination_directory + '_rotated'):
        os.makedirs(destination_directory + '_rotated')
    
    for i in range(len(im_paths)):

        M = computeUnRotMatrix(
            df.yaw[i],
            df.pitch[i],
            df.roll[i]
        )

        correctedImage = warpPerspectiveWithPadding(cv2.imread(im_paths[i]), M)
        
        res =transparency(correctedImage)
        cv2.imwrite(destination_directory + '_rotated' +'/'+ str(i).zfill(3) + '.png', res)
