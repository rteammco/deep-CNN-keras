# Handles processing image path files (which define where the data is stored)
# and provides a loader that reads and stores the training and test data in
# memory to be fed into a neural network.

from keras.utils import np_utils
import numpy as np
from PIL import Image


class ImageInfo(object):
  """Loads image file paths from input files."""

  self._DEFAULT_IMG_DIMENSIONS = (256, 256, 1)

  def __init__(self, num_classes, num_train_imgs_per_class,
               num_test_imgs_per_class):
    """Sets up the initial data variables and data set sizes.

    Args:
      num_classes: the number of data classes in the data set.
      num_train_imgs_per_class: the number of training images provided for each
          class. The number of images must be the same for each class. For
          example, if this number is 100, then for each of the 'num_classes'
          classes, exactly 100 training images must be provided.
      num_test_imgs_per_class: similarly, the number of test images per class.
    """
    # Set the data size values.
    self.num_classes = num_classes
    self.num_train_imgs_per_class = num_train_img_per_class
    self.num_test_imgs_per_class = num_test_img_per_class
    # Initialize the data lists.
    self.img_dimensions = self._DEFAULT_IMG_DIMENSIONS
    self.classnames = []
    self.train_img_files = []
    self.test_img_files = []

  def set_image_dimensions(self, width, height, num_channels):
    """Set the training and testing image dimensions.
    
    All images fed into the neural network, for training and testing, will be
    formatted to match these dimensions.

    Args:
      width: a positive integer indicating the width of the images.
      height: a positive integer indicating the height of the images.
      num_channels: the number of channels to use. This number should be 1
          for grayscale training images or 3 to train on full RGB data.
    """
    # Make sure all the data is valid.
    if width <= 0:
      width = self._DEFAULT_IMG_DIMENSIONS[0]
    if height <= 0:
      height = self._DEFAULT_IMG_DIMENSIONS[1]
    if num_channels not in [1, 3]:
      num_channels = self._DEFAULT_IMG_DIMENSIONS[2]
    # Set the dimensions.
    self.img_dimensions = (width, height, num_channels)

  def load_image_classnames(self, fname):
    """Reads the classnames for the image data from the given file.
    
    Each class name should be on a separate line.

    Args:
      fname: the name of the file containing the list of class names.
    """
    self._read_file_data(fname, self.classnames)

  def load_train_image_paths(self, fname):
    """Reads the image paths for the training data from the given file.
    
    Each file name (full directory path) should be on a separate line. The file
    paths must be ordered by their class label.

    Args:
      fname: the name of the file containing the training image paths.
    """
    self._read_file_data(fname, self.train_img_files)

  def load_test_image_paths(self, fname):
    """Reads the image paths for the test data from the given file.
    
    Each file name (full directory path) should be on a separate line. The file
    paths must be ordered by their class label.

    Args:
      fname: the name of the file containing the test image paths.
    """
    self._read_file_data(fname, self.test_img_files)

  def _read_file_data(self, fname, destination):
    """Reads the data of the given file into the destination list.
    
    The file will be read line by line, and each line that doesn't start with a
    "#" or is not empty will be stored in the given list.

    Args:
      fname: the name of the file to read.
      destination: a list into which the file's data will be put line by line.
    """
    paths_file = open(fname, 'r')
    for line in paths_file:
      impath = line.strip()
      if len(impath) == 0 or impath.startswith('#'):
        continue
      destination.append(impath)
    paths_file.close()


class ImageLoader(object):
  """Loads image data from provided image paths."""

  def __init__(self, image_info):
    """Reads in all of the images as defined in the given ImageInfo object.

    Args:
      image_info: an ImageInfo object that contains all of the image paths
          and data size values. These images will be loaded into memory and
          used for training and testing.
    """
    # Data size information:
    self._image_info = image_info
    num_classes = self._image_info.num_classes
    img_w = self._image_info.img_dimensions[0]
    img_h = self._image_info.img_dimensions[1]
    num_channels = self._image_info.img_dimensions[2]
    # Initialize the empty train data arrays:
    num_train_imgs = num_classes * self._image_info.num_train_imgs_per_class
    self.train_data = np.empty((num_train_imgs, num_channels, img_w, img_h),
                               dtype='float32')
    self.train_labels = np.empty((num_train_imgs,), dtype='uint8')
    # Initialize the empty test data arrays:
    num_test_imgs = num_classes * self._image_info.num_test_imgs_per_class
    self.test_data = np.empty((num_test_imgs, num_channels, img_w, img_h),
                              dtype='float32')
    self.test_labels = np.empty((num_test_imgs,), dtype='uint8')

  def load_train_images(self):
    """..."""
    self._load_images(
        self._image_info.train_img_files,
        self._image_info.num_train_imgs_per_class,
        self.train_data, self.train_labels, 'train')
    self._load_images(
        self._image_info.test_img_files,
        self._image_info.num_test_imgs_per_class,
        self.test_data, self.test_labels, 'test')
    # Normalize the data as needed:
    train_data = train_data.astype('float32') / 255
    test_data = test_data.astype('float32') / 255
    train_labels = np_utils.to_categorical(train_labels, num_categories)
    test_labels = np_utils.to_categorical(test_labels, num_categories)

  def _load_images(self, file_names, num_per_class, data, labels, disp):
    """Reads all images."""
    image_index = 0
    label_id = -1
    for impath in file_names:
      if image_index % num_per_class:
        label_id += 1
        print 'Loading {} images for class "{}"...'.format(
            disp, self._image_info.classnames[label_id])
      img = Image.open(impath)
      img = img.resize((self._image_info.img_dimensions[0],
                        self._image_info.img_dimensions[1]))
      # TODO: convert only if channel = 1... otherwise, if the image is already
      # grayscale, replicate the intensities into 3 channels.
      img = img.convert('L')
      img_arr = np.asarray(img, dtype='float32')
      data[image_index, 0, :, :] = img_arr
      labels[image_index] = label_id
      image_index += 1
