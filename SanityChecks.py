import enum
from PIL import Image
from os.path import splitext
from os import pathsep


# Error codes that can result from validating a ppm file
class PPMCodes(enum.Enum):
    BAD_DIMENSIONS = 1
    BAD_DEPTH = 2
    NOT_PPM3 = 3
    NOT_PPM = 4
    GOOD = 5
    BAD = 6


def check_image_size_consistency_ppm(images, verbose=False, fullpath=False):
    """
    Ensures that all ppm files in an image collection retrieved by retrieve_valid_files are all the same size.
    This is the sister function to check_image_size_consistency_ppm_required_size differing only in the fact
    that it does not ensure a specific size, but checks for discrepancies between each and all files.

    As such, the runtime of this function is much longer
    :param images: The collection retrieved by retrieve_valid_files
    :param verbose: Determines whether or not to print out error messages
    :param fullpath: Determines whether or not in the error message will print out the involved files' path or name
    :return: A boolean indicating if all ppms files are equal in size (true) or there is at least one difference (false)
    """
    # Flag that is set to True if something goes wrong
    is_ok = True
    # For every image in the collection
    for img in images:
        # Make sure the ppm is actually valid before we attempt to open it up and use it
        if valid_ppm(img, verbose=verbose) == PPMCodes.GOOD:
            # Open up the file and extract the dimensions
            with open(img) as file:
                lines = file.readlines()
                lines = [x.strip('\n') for x in lines]
                dimensions = lines[1].split()
                w = float(dimensions[0])
                h = float(dimensions[1])
                size = (w, h)
            # For every other image in the collection
            for img2 in images:
                # Make sure hte ppm is valid
                if valid_ppm(img, verbose=verbose):
                    with open(img) as file:
                        # Get the dimensions for the ppm image
                        lines = file.readlines()
                        lines = [x.strip('\n') for x in lines]
                        dimensions = lines[1].split()
                        w = float(dimensions[0])
                        h = float(dimensions[1])
                        # If the sizes don't match we set our flag and printout the files and their dims
                        if size[0] * size[1] != w * h:
                            is_ok = False
                            if fullpath and verbose:
                                print('{} does not match {} in size ({} vs {})'.format(img, img2, size, (w, h)))
                            elif verbose and not fullpath:
                                print('{} does not match {} in size ({} vs {})'.format(img.split('\\').pop(),
                                                                                       img2.split('\\').pop(),
                                                                                       size, (w, h)))
    return is_ok


def check_image_size_consistency_ppm_required_size(images, required_size, verbose=False, fullpath=False):
    """
    Ensures that all ppm files in an image collection retrieved by retrieve_valid_files are all the same size.
    This is the sister function to check_image_size_consistency_ppm_ differing only in the fact
    that it ensures a specific size across all files
    :param images: The collection retrieved by retrieve_valid_files
    :param required_size: The size required (width * height) in pixels
    :param verbose: Whether or not to print out error messages as we go through the files
    :param fullpath: Whether or not to print out full file path or just name when being verbose
    :return: True if all files match the required size, false otherwise
    """
    is_ok = True
    # For every image in the collection
    for img in images:
        # Open up the image, make sure its valid, and retrieve its dimensions
        with open(img) as file:
            if valid_ppm(img, verbose=verbose) == PPMCodes.GOOD:
                lines = file.readlines()
                lines = [x.strip('\n') for x in lines]
                dimensions = lines[1].split()
                w = float(dimensions[0])
                h = float(dimensions[1])
                # If the total size is not equal to the required size, print out an error message
                if w * h != required_size:
                    is_ok = False
                    if verbose:
                        if fullpath:
                            print('{} does not have the require size of {} (has size of {})'
                                  .format(img, required_size, w * h))
                        else:
                            print('{} does not have the require size of {} (has size of {})'
                                  .format(img.split('\\').pop(), required_size, w * h))

    return is_ok


def check_image_size_consistency_generic(images, verbose=False, fullpath=False):
    """
    Checks if all img files contianed within 'images' are all equal in size
    :param images: Return value from retrieve_valid_files
    :param verbose: Whether or not to print out errors in sizes as we find them
    :param fullpath: Whether or not to print out full path or just file name in our verbosity
    :return:
    """
    is_ok = True
    # The img files in the images collection are just paths. We can't ascertain their sizes without some help from PIL
    generic = {}
    for img in images:
        generic[img] = Image.open(img)
    # The keys will be the paths, will the values will be the images themselves (a PIL class)
    keys = generic.keys()
    for i in keys:
        imgi = generic[i]
        size = imgi.size
        for j in keys:
            imgj = generic[j]
            if generic[j].size[0] != size[0] or generic[j].size[1] != size[1]:
                is_ok = False
                if verbose:
                    if not fullpath:
                        print('{} does not match {} in size ({} vs {})'
                              .format(i.split('\\').pop(), j.split('\\').pop(), (imgj.width, imgj.height), size))
                    else:
                        print('{} does not match {} in size ({} vs {})'
                              .format(i, j, (imgj.width, imgj.height), size))
    return is_ok


def check_image_size_consistency_generic_required_size(images, required_size, verbose=False, fullpath=False):
    """
    Checks to see if all img files in 'images' are equal to the specified required size
    :param images: Collection of paths returned by retrieve_valid_files
    :param required_size: The total size in pixels that the images must be equal to
    :param verbose: Whether or not to print out errors in sizes as we find them
    :param fullpath: Whether or not to print out full path or just file name in our verbosity
    :return:
    """
    is_ok = True
    generic = {}
    # The img files in the images collection are just paths. We can't ascertain their sizes without some help from PIL
    for img in images:
        generic[img] = Image.open(img)
    # The keys will be the paths, will the values will be the images themselves (a PIL class)
    for i in generic.keys():
        img = generic[i]
        if img.width * img.height != required_size:
            is_ok = False
            if verbose:
                if not fullpath:
                    print('{} does not have the require size of {} (has size of {})'
                          .format(i.split('\\').pop(), required_size, img.width * img.height))
                else:
                    print('{} does not have the require size of {} (has size of {})'
                          .format(i, required_size, img.width * img.height))
    return is_ok


def valid_ppm(path, verbose=False, fullpath=False, return_error_codes=False):
    """
    Checks to make sure a specific ppm file is actually a valid ppm file by checking the following:
        The file has the extension .ppm
        The first line is the 'magic number': P3
        The second line's dimensions (w x h) equals the actual size of the file
        The third line is the color depth and it should be '255'
    The function keeps a running collection of the errors gotten, and can return that collection if wanted
    Otherwise it will return True if all tests are pass, and false if any are failed
    :param path: The path to the ppm file
    :param verbose: Whether or not to print out error messages as we fail tests
    :param fullpath: Whether or not to print out the file's full path when printing out errors
    :param return_error_codes: Whether or not to return the collection of errors
    :return: True/False or a list holding PPMCodes
    """
    # Keep track of our errors in case we need to return them
    errors = []
    # Since we have the path, we need single out the filename to ensure it ends with .ppm
    filename = path.split(pathsep).pop()
    suffix = splitext(filename)[1]
    if suffix != '.ppm':
        if verbose:
            if fullpath:
                print('{} is not even a ppm file (has extension {}'.format(path, suffix))
            else:
                print('{} is not even a ppm file (has extension {}'.format(filename, suffix))
        errors.append(PPMCodes.NOT_PPM)
        if return_error_codes:
            return errors
        else:
            return False
    # Open the file, read the lines, strip the lines of all newlines (to ensure proper equality checks) and extract
    # the dimensions
    with open(path) as file:
        lines = file.readlines()
        lines = [x.strip('\n') for x in lines]
        dimensions = lines[1].split()
        w = float(dimensions[0])
        h = float(dimensions[1])
        # Perform basic equality checks
        if lines[2] != '255':
            if verbose:
                if fullpath:
                    print('{} does not have the correct color depth of 255 (has {})'.format(path, lines[3]))
                else:
                    print('{} does not have the correct color depth of 255 (has {})'.format(filename, lines[3]))
                errors.append(PPMCodes.BAD_DEPTH)
        if lines[0] != 'P3':
            if verbose:
                if fullpath:
                    print('{} does not have the correct magic number of P3 (has {})'.format(path, lines[0]))
                else:
                    print('{} does not have the correct magic number of P3 (has {})'.format(filename, lines[0]))
            errors.append(PPMCodes.NOT_PPM3)
        # Have to multiply by three because the width * height will be total number of pixels, while the length of the
        # lines list from index 3 onward will be all the rgb values for the pixels. So one pixel takes up three lines
        # in a ppm file
        if len(lines[3:]) != (w * h) * 3:
            if verbose:
                if fullpath:
                    print('{} does not have the correct size: {} != {}'.format(path, len(lines[3:]), (w*h)/3))
                else:
                    print('{} does not have the correct size: {} != {}'.format(filename, len(lines[3:]), (w * h) / 3))
            errors.append(PPMCodes.BAD_DIMENSIONS)
    if return_error_codes:
        return PPMCodes.GOOD if not errors else PPMCodes.BAD
    else:
        return errors
