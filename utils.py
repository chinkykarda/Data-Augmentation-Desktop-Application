'''
This file contains utility functions/classes for image transformations.

Image Class: This class provides utility to load an image and perform transformations
    Methods:
        1. transform
        2. rotate
        3. scale
        4. translate_horizontal
        5. flip
        6. shear
        7. getImage
'''

import cv2 as cv # OpenCV prefers importing cv2 as cv standard
import numpy as np
import os # For file handling
import sys
import random

class Image:
    '''
    This Image class is a utility class to help load, and transform an input image
    '''
    def __init__(self, path='extras/00004IMG_00004_BURST20190912100717.jpg'):
        '''
        Paramaters
        ========
        1. path: (default = 'extras/sample.jpg')
        '''

        self.image = cv.imread(path,1) # Load as a colored image
        # available_transforms dictionary assigns function to the input
        # transform
        self.available_transforms = {
            # 'shear': self.shear,
            'rotate': self.rotate,
            'translate': self.translate_horizontal,
            'scale': self.scale,
            'flip': self.flip,
            'shear': self.shear
        }
        #print(path)
        ##print(self.image.shape)
        if (self.image is None):
            #print("Image not found, please check the path ({})".format(path))
            #print("Exiting...")
            sys.exit(0)

    def transform(self, transform, bounding_box = None, factor = 0):
        '''
        Paramaters
        ========
        1. transform: (str) options available: 'shear', 'rotate', 'translate',
                                               'scale', 'flip'
        2. bounding_box (list) format - [top left x, top left y, bottom right x, bottom right y]

        Returns
        ========
        A list of:
        1. Transformed Image (np.array)
        2. Bounding Boxes (list)
        '''
        factor = float(factor)
        if (bounding_box is None):
            bounding_box = self.crop()
            #print("got: ", bounding_box)

        if (transform in self.available_transforms.keys()):
            R = self.available_transforms[transform](bounding_box, factor)
            return R
        else:
            #print("Transform not available. Available transforms: {}".format(self.available_transforms.keys()))
            #print("Exiting...")
            sys.exit(0)

    def rotate(self, bounding_box, angle=45):
        '''
        Utility function that performs rotation on self.image object
        Returns transformed image and bounding box

        Paramaeters
        ======
        1. bounding_box (list) format - [top left x, top left y, bottom right x, bottom right y]
        2. angle (int, default=45) angle to rotate an image with

        Returns
        ======
        1. Transformed Image (np.ndarray)
        2. (transformed) Bounding Box coordinates (list)
        '''
        
        height, width = self.image.shape[0],self.image.shape[1]
        # (width/2, height/2) is the center of our image - around which rotation is performed
        matrix = cv.getRotationMatrix2D(center = (width/2, height/2), angle = angle, scale = 1.0)
        rotated_image = cv.warpAffine(self.image, matrix, (width, height))

        rotated_point_A = np.matmul( matrix, np.array( [bounding_box[0], bounding_box[1], 1] ).T )
        rotated_point_B = np.matmul( matrix, np.array( [bounding_box[2], bounding_box[1], 1] ).T )
        rotated_point_C = np.matmul( matrix, np.array( [bounding_box[2], bounding_box[3], 1] ).T )
        rotated_point_D = np.matmul( matrix, np.array( [bounding_box[0], bounding_box[3], 1] ).T )

        # Compute new bounding box, that is, the bounding box for rotated object
        x = np.array( [ rotated_point_A[0], rotated_point_B[0], rotated_point_C[0], rotated_point_D[0] ] )
        y = np.array( [ rotated_point_A[1], rotated_point_B[1], rotated_point_C[1], rotated_point_D[1] ] )
        new_bounding_box = [np.min( x ).astype(int), np.min( y ).astype(int), np.max( x ).astype(int), np.max( y ).astype(int)]

        return [rotated_image, new_bounding_box]

    def scale(self, bounding_box, scale_by = 0.5):
        '''
        Performs scaling transformation

        Parameters
        =======
        1. bounding_box (list) format - [top left x, top left y, bottom right x, bottom right y]
        2. scale_by (default = 0.5)

        Returns
        ========
        Returns a list of:
        1. Scaled Image (np.array)
        2. New Bounding Box Coordinates
        '''

        height, width = self.image.shape[0],self.image.shape[1]
        scaled_width = int(scale_by * width)
        scaled_height = int(scale_by * height)

        dst = cv.resize(self.image, (scaled_width, scaled_height))

        matrix = np.array([[scale_by, 0, 0], [0, scale_by, 0], [0, 0, scale_by]])
        bounding_box_top_left = np.matmul(matrix, np.array([bounding_box[0], bounding_box[1], 1]).T)
        bounding_box_bottom_right = np.matmul(matrix, np.array([bounding_box[2], bounding_box[3], 1]).T)

        new_boundingbox = [bounding_box_top_left[0].astype(int), bounding_box_top_left[1].astype(int), \
            bounding_box_bottom_right[0].astype(int), bounding_box_bottom_right[1].astype(int)]

        return dst, new_boundingbox

    def translate_horizontal(self, bounding_box, shift_by=0.2):
        '''
        Performs translate horizontal

        Parameters
        =======
        1. bounding_box (list) format - [top left x, top left y, bottom right x, bottom right y]
        2. shift_by (default=0.2)

        Returns
        ========
        Returns a list of:
        1. Translated Image (np.array)
        2. New Bounding Box Coordinates
        '''

        
        img_height, img_width = self.image.shape[0],self.image.shape[1]
        factor = img_width * shift_by

        M = np.float32([[1,0,factor],[0,1,0]])
        shifted_image = cv.warpAffine(self.image, M, (img_width, img_height) )

        # compute new bounding box
        shifted_point_A = np.matmul( M, np.array( [bounding_box[0], bounding_box[1], 1] ).T )
        shifted_point_C = np.matmul( M, np.array( [bounding_box[2], bounding_box[3], 1] ).T )

        new_boundingbox = [ shifted_point_A[0].astype(int), shifted_point_A[1].astype(int),
                            shifted_point_C[0].astype(int), shifted_point_C[1].astype(int) ]

        return shifted_image, new_boundingbox

    def flip(self, bounding_box,factor):
        '''
        Performs flip horizontal

        Parameters
        =======
        1. bounding_box (list) format - [top left x, top left y, bottom right x, bottom right y]

        Returns
        ========
        Returns a list of:
        1. Flipped Image (np.array)
        2. New Bounding Box Coordinates
        '''
        flipHorizontal = cv.flip(self.image, 1)

        img_center = np.array(self.image.shape[:2])[::-1]/2
        img_center = np.hstack((img_center, img_center))
        ##print("image_center: ",img_center)
        # Compute new Bounding Box coordinates
        bounding_box = np.array(bounding_box)
        # #print(bounding_box[[0, 2]])
        img_center = np.array([int(x) for x in img_center])
        # #print(img_center[[0,2]])
        bounding_box[[0,2]] += 2*(img_center[[0,2]] - bounding_box[[0,2]])

        box_w = abs(bounding_box[0] - bounding_box[2])

        bounding_box[0] -= box_w
        bounding_box[2] += box_w

        return [flipHorizontal, bounding_box]

    def shear(self, bounding_box, factor ):
        shear_factor=(-factor, factor)
        shear_factor = random.uniform(*shear_factor)
        image_width, image_height = self.image.shape[1], self.image.shape[0]

        matrix = np.array([[1, abs(shear_factor), 0],[0,1,0]])

        new_width =  self.image.shape[1] + abs(shear_factor*self.image.shape[0])

        bounding_box = np.array(bounding_box)
        new_bounding_box = bounding_box
        new_bounding_box[[0,2]] += ((bounding_box[[1,3]]) * abs(shear_factor) ).astype(int)

        img = cv.warpAffine(self.image, matrix, (int(new_width), self.image.shape[0]))
        img = cv.resize(img, (image_width, image_height))
        scale_factor_x = new_width / image_width
        new_bounding_box = np.array([float(x) for x in new_bounding_box])
        new_bounding_box /= [scale_factor_x, 1, scale_factor_x, 1]

        new_bounding_box = [int(x) for x in new_bounding_box] # Convert all to int, OpenCV understands integers for pixel coords
        return [img, new_bounding_box]

    def getImage(self):
        '''
        Returns the image loaded by utility function
        '''
        return self.image


class RandomHSV(object):
    """HSV Transform to vary hue saturation and brightness

    Hue has a range of 0-179
    Saturation and Brightness have a range of 0-255.
    Chose the amount you want to change thhe above quantities accordingly.




    Parameters
    ----------
    hue : None or int or tuple (int)
        If None, the hue of the image is left unchanged. If int,
        a random int is uniformly sampled from (-hue, hue) and added to the
        hue of the image. If tuple, the int is sampled from the range
        specified by the tuple.

    saturation : None or int or tuple(int)
        If None, the saturation of the image is left unchanged. If int,
        a random int is uniformly sampled from (-saturation, saturation)
        and added to the hue of the image. If tuple, the int is sampled
        from the range  specified by the tuple.

    brightness : None or int or tuple(int)
        If None, the brightness of the image is left unchanged. If int,
        a random int is uniformly sampled from (-brightness, brightness)
        and added to the hue of the image. If tuple, the int is sampled
        from the range  specified by the tuple.

    Returns
    -------

    numpy.ndaaray
        Transformed image in the numpy format of shape `HxWxC`

    numpy.ndarray
        Resized bounding box co-ordinates of the format `n x 4` where n is
        number of bounding boxes and 4 represents `x1,y1,x2,y2` of the box

    """

    def __init__(self, hue=None, saturation=None, brightness=None):
        if hue:
            self.hue = hue
        else:
            self.hue = 0

        if saturation:
            self.saturation = saturation
        else:
            self.saturation = 0

        if brightness:
            self.brightness = brightness
        else:
            self.brightness = 0

        if type(self.hue) != tuple:
            self.hue = (-self.hue, self.hue)

        if type(self.saturation) != tuple:
            self.saturation = (-self.saturation, self.saturation)

        if type(brightness) != tuple:
            self.brightness = (-self.brightness, self.brightness)

    def __call__(self, img, bboxes):

        hue = random.randint(*self.hue)
        saturation = random.randint(*self.saturation)
        brightness = random.randint(*self.brightness)

        img = img.astype(int)

        a = np.array([hue, saturation, brightness]).astype(int)
        img += np.reshape(a, (1, 1, 3))

        img = np.clip(img, 0, 255)
        img[:, :, 0] = np.clip(img[:, :, 0], 0, 179)

        img = img.astype(np.uint8)

        return img, bboxes
