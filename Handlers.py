import os
import ImageUtils
import SanityChecks


def handleppm(filename="__slicedimage__", path="", save_dir="", left_right=False):
    """
    A handler that takes care of slicing a set of ppm images.
    Note that this function does NOT perform the actual slicing, but simply takes user input, validates it, and calls
    the proper functions to accomplish the slicing, all while providing user feedback on operation status
    :param left_right: A boolean value that will be passed to the actual slicing functions
    :param path: Path from which to retrieve the image files.
    :param filename: Name we are going to give the sliced image
    :param save_dir: The directory we are going to save the sliced image in
    :return: The directory that the new file was saved in, and the new file's name
    """
    # Empty file var that will eventually hold the new file's name
    file = None
    # File name is only set if valid, so the var will not be 'None' when all the checks are passed
    if save_dir == "":
        save_dir = path
    else:
        if not os.path.exists(save_dir):
            print("Invalid save directory: {}".format(save_dir))
            exit(1)

    if os.path.splitext(filename)[1] != '.ppm':
        filename += '.ppm'
    if save_dir.endswith('\\') or save_dir.endswith('/'):
        try:
            file = open(save_dir + filename, 'w')
        except OSError as e:
            print(e)
            exit(1)
    else:
        try:
            file = open(save_dir + "\\" + filename, 'w')
        except OSError as e:
            print(e)
            exit(1)
    # Now that we have a proper filename we can begin the actual slicing process
    while True:
        # Get the path that we will retrieve the images from

        # Retrieve our ppm images from the path specified. Our retrieval function checks if the path exists for us
        # If the path does not exist the return value will default to None
        images = ImageUtils.retrieve_valid_files(path, False, '.ppm')
        # If we got None as a return value, then the directory was invalid
        if images is None:
            print()
            print('Invalid directory: {}'.format(path))
            print()
            continue
        # If the return value is an empty list then obviously we can't move to slicing so we let the user retry
        if not images:
            print()
            print("No images in the directory were retrieved. Try another")
            print()
            continue
        # Check if all the images are equal in size using our util function. Let verbose be true so we don't have to
        # handle telling the user their wrongdoings
        print('Making sure that all images are equal in size . . .')
        # The utility function returns either True or False so we can continue to slicing or not based on its call
        if SanityChecks.check_image_size_consistency_ppm(images, verbose=True):
            # The image slicing function does not save anything, but only returns the new image data
            print('Slicing the images now . . .')
            imgdata = ImageUtils.create_blend_ppm(images, left_right)
            # Save the data returned by the function
            file.write(imgdata)
            file.close()
            # Return the current working directory as the save dir and the file name
            return save_dir, file.name


def handlegeneric(filename="__slicedimage__", path="", save_dir="", ftype="", left_right=False):
    """
    A handler that takes care of slicing a set of jpg/jpeg images.
    Note that this function does NOT perform the actual slicing, but simply takes user input, validates it, and calls
    the proper functions to accomplish the slicing, all while providing user feedback on operation status
    :param left_right: A boolean value that will be passed to the actual slicing functions
    :param path: Path from which to retrieve the image files.
    :param filename: Name we are going to give the sliced image
    :param save_dir: The directory we are going to save the sliced image in
    :param ftype: File type
    :return: The directory that the new file was saved in, and the new file's name
    """
    if ftype == 'jpg':
        ftype = 'jpeg'
    if save_dir == "":
        save_dir = path
    else:
        if not os.path.exists(save_dir):
            print("Invalid save directory: {}".format(save_dir))
            exit(1)
    # Get the filename from the user

    # Ensure that the extension is a valid jpe extension

    while True:
        # Get the path where the jpgs are

        # Retrieve the jpg files from the directory (path checking is cooked into the function itself)
        images = ImageUtils.retrieve_valid_files(path, False, '.jpg', '.jpeg')
        if images is None:
            print()
            print('Invalid directory: {}'.format(path))
            print()
            continue
        # If we didn't get any images let the user know and retry
        if not images:
            print()
            print("No images in the directory were retrieved. Try another")
            print()
            continue
        # Check if all the images are the same size
        print('Making sure that all images are equal in size . . .')
        if SanityChecks.check_image_size_consistency_jpg(images, verbose=True):
            # Slice the images and save the new one
            print('Slicing the images now . . .')
            img = ImageUtils.create_blend_generic(images, left_right)
            if save_dir.endswith('\\') or save_dir.endswith('/'):
                img.save(save_dir + filename + '.' + ftype.lower(), ftype)
            else:
                img.save(save_dir + '\\' + filename + '.' + ftype.lower(), ftype)

            # Return the current working directory (thats where we saved the new file) and the new file name
            return save_dir, filename
