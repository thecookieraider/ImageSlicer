import os
from PIL import Image


def create_blend_generic(images, left_right=True):
    """
    Blends together even slices from a collection of jpgs to form one image. Function can slice to form a transition
    going top-down or left to right

    This function assumes that all jpg images are of the same size and mode
    :param images: Collection of paths to jpgs
    :param left_right: Whether or not the transition will be left to right or top to bottom
    :return: A PIL Image class of the new image
    """
    # The way the slicing is performed is through PIL's cropping method. We simply takes equal crops from each
    # image and stitch them together to form a new one
    imagesl = []
    croppedjpgs = []
    # The images collection is just a list of paths. We need PIL classes to crop
    for img in images:
        imagesl.append(Image.open(img))
    # Used to determine how much to take from each image
    divisor = len(imagesl)
    # Leftoff is our 'marker' variable. Will be used to determine where to start and stop on a particular image when
    # cropping
    leftoff = 0
    # Get the jpg attributes so we can apply them to the new image
    w, h, mode, size = imagesl[0].width, imagesl[0].height, imagesl[0].mode, imagesl[0].size
    # If we are going left to right, the leftoff variable will go from left to right with respect to width
    # If we are going top down, the leftoff variable will go from top to bottom with respect to height
    c_w = int(w / divisor)
    c_h = int(h / divisor)
    if left_right:
        for i in imagesl:
            # Crop the image we are currently on using leftoff to determine the bounds for the left and right
            # (top and bottom remain constant)
            croppedjpgs.append(i.crop((leftoff, 0, int(leftoff + c_w) % (w+1), h)))
            # Move the boundaries
            leftoff = ((leftoff + c_w) % w)
        # Setup a new image
        new_img = Image.new(mode, size)
        # Reset the bounds
        leftoff = 0
        # This is the same process as the cropping, except we're just pasting now
        for cropped in croppedjpgs:
            new_img.paste(cropped, (int(leftoff), 0, int(leftoff + c_w) % (w+1), h))
            leftoff = ((leftoff + c_w) % w)
    # Top down process is the exact same as left right except the left and right bounds remain constant, and the top
    # and bottom bounds change (using leftoff)
    else:
        for i in imagesl:
            croppedjpgs.append(i.crop((0, int(leftoff), w, int(leftoff + c_h) % (h + 1))))
            leftoff = ((leftoff + c_h) % h)
        new_img = Image.new(mode, size)
        leftoff = 0
        for cropped in croppedjpgs:
            new_img.paste(cropped, (0, int(leftoff), w, int(leftoff + (h / divisor)) % (h + 1)))
            leftoff = ((leftoff + c_h) % h)
    # Return the new image (PIL class)
    return new_img


def get_pixel_data(image):
    """
    Provides structure for accessing a ppm files data in the form of a dictionary. The dictionary returned can be used
    by providing a tuple in the form (y, x) to receive the pixel's rgb data at that point (y is the row, x is the col)
    :param image: Path to a ppm file
    :return: A dictionary mapping tuples of (y, x) pairs to a tuple of (r, g, b)
    """
    data = dict()
  
    with open(image) as i:
        # Extract the dimensions and all the lines past the first three
        lines = i.readlines()
        w, h = int(lines[1].split()[0]), int(lines[1].split()[1])
        col = lines[3:]
        x = y = 0
        # We loop over the lines three at a time
        for rgb in zip(col[0::3], col[1::3], col[2::3]):
            # Setup a key value pair
            data[(x, y)] = rgb
            # Increase the y (going forward one column)
            y += 1
            # If we are out of bounds
            if y > w-1:
                # Go back to column one and increase the row
                y = 0
                x += 1
    return data


def extract_ppm_data(image):
    """
    Basic utility function that just returns a dictionary mapping basic ppm attributes to their values
    :param image: Path to a ppm file
    :return: Dictionary mapping string attributes to values
    """
    d = {}
    with open(image) as f:
        lines = f.readlines()
        dims = lines[1].split()
        depth = lines[2]
        magic_no = lines[0]
        w = int(dims[0])
        h = int(dims[1])
        d['width'] = w
        d['height'] = h
        d['depth'] = depth
        d['magic_number'] = magic_no
        d['header'] = lines[:3]
    return d


def create_blend_ppm(images, left_right=True):
    """
    Blends together even slices from a collection of ppms to form one image. Function can slice to form a transition
    going top-down or left to right

    This function builds a new image by taking crops from each parent image in a left to right fashion.
    Since ppm files are structured in such a way that the first pixel in a ppm file is the first pixel on the first
    row, and the second pixel is the second pixel on the first row etc., we need to build a image from left to right,
    moving down rows as we reach the furthest point right

    Both top-down and left-right transitions are formed using this same technique. The difference is that for top-down,
    you don't build rows from pieces of each parent image, you just take entire chunks from each parent image
    so that the final image is parent1chunk+parent2chunk+parent3chunk

    A graphical representation helps

    Assume you have three images:

    |abcdefghi| |123456789| |a1b2c3d4e|
    |jklmnopqr| |246813579| |f5g6h7i8j|
    |stuvwxyz_| |987654321| |k9l1m2n3o|

    Going from left to right you would form the new image like so:

    |abc 456 d4e| Notice how we just take the first third of the first image, second third of the second image, and
    |jkl 813 i8j| the final third from the third image. This scales easily with more images, just decrease slice ratio
    |stu 654 n3o| (4 images would mean 1/4, 5 images is 1/5 etc.)

    Going from top to bottom would look like such:
    |abcdefghi| We just copy entire rows from the parent images. So the first third of rows of the final image should
    |246813579| be the first thrid of rows from the first parent image etc.
    |k9l1m2n3o|

    This function assumes that all ppm images are of the same size, and that they are all valid ppm files

    :param images: List of paths to valid ppm files
    :param left_right: Whether or not the blend transition will be left to right or top down (if false)
    :return: A string holding the new ppm image data
    """
    new_image_data = []
    # Used to determine how much to take from each image
    divisor = len(images)
    # Leftoff is our 'marker' variable. Will be used to determine where to start and stop on a particular image when
    # cropping
    leftoff = 0
    if left_right:
        # Extract image data
        img_data = extract_ppm_data(images[0])
        # Save the width, height and append the header onto the end of the new image
        width = img_data['width']
        height = img_data['height']
        new_image_data += img_data['header']
        # Get pixel data so we can actually use y,x pairs
        datas = [get_pixel_data(img) for img in images]
        # Go from top row to bottom row
        for h in range(int(height)):
            # We're going to crop a piece from each image
            for d in datas:
                # Go only up until the bounds specified and then increase the bounds, paying respect to the width
                # using modulus to ensure no out of bounds errors
                for w in range(int(leftoff) % width, int(leftoff + (width / divisor)) % (width+1)):
                    new_image_data.append(''.join(d[(h, w)]))
                leftoff = (leftoff + (width / divisor)) % width
    # Top down is much easier than left-right, we just have to copy chunks, so we don't even need the
    # datas, we just do simple string manipulation
    else:
        for img in images:
            with open(img) as file:
                lines = file.readlines()
                new_image_data += lines[int(leftoff):int(leftoff + (len(lines) / divisor))]
                leftoff += len(lines) / divisor
    return ''.join(new_image_data)


def retrieve_valid_files(path, go_deep=False, *suffixes):
    """
    Retrieves files with the specified suffixes. Multiple suffixes are allowed. If go_deep is specified the function
    checks lower folders for hte proper files
    :param path: Path to a directory
    :param go_deep: Boolean indicating if the function should check lower and lower folders
    :param suffixes: Proper file suffixes
    :return: A list of paths to valid folders
    """
    path = path.replace('/', '\\')
    # Keeping a list of found, valid files
    files = []
    # Directories will only be used if go-deep is specified
    directories = [path]
    while directories:
        # Pop the latest directory
        currdir = directories.pop()
        # If that directory does exist (in place for the user-specified dir)
        if os.path.exists(currdir):
            # Try to scan it
            try:
                file_list = list(os.scandir(currdir))
                for i in file_list:
                    # If we aren't going deep we just check for file and if tit has hte suffix we need we append.
                    # If no suffixes are specified we grab all the files found
                    if not go_deep:
                        if i.is_file():
                            if not suffixes:
                                files.append(i.path)
                            else:
                                if os.path.splitext(i.name)[1] in suffixes:
                                    files.append(i.path)
                    # Go deep was specified, so for each directory found we append it to the directory list for later
                    # iteration
                    else:
                        if i.is_dir():
                            directories.append(i.path)
                        # Same file checking as above
                        elif i.is_file():
                            if not suffixes:
                                files.append(i.path)
                            else:
                                if os.path.splitext(i.name)[1] in suffixes:
                                    files.append(i.path)
            # Windows can be tricky sometimes in terms of folder access, so if we get an error, we just print and move
            # to the next dir
            except WindowsError as e:
                print(e)
        # If the initial dir is invalid, we can't do anything, so we return None
        else:
            return None
    # Return the files sorted alphabetically
    return sorted(files)

