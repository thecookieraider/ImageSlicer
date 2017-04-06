from Handlers import *
import sys
import getopt
import random

# Valid image formats that the program can handle. Should be in same order as they appear in the VALID_SELECTIONS dict
VALID_FORMATS = ['ppm', 'jpg', 'jpeg', 'png']
METHOD_KEY = {'1': True, '2': False}

HELP = "-h - Prints this\n"\
       "-s <directory> - Directory to retrieve the source images from\n"\
       "-d <directory> - Destination in which the newly sliced image will be placed (defaults" \
       " to path where we source our images from)\n"\
       "-t <filetype> - Type of image file that will be sliced\n" \
       "\t\tAvailable types:\n\t\t" + '\n\t\t'.join(VALID_FORMATS) + '\n'\
       "-m <1|2> - Method to use when slicing. 1: Final image will be composed of horizontal slices" \
       " 2: Final image will be composed of vertical slices\n" \
       "-n - Optional parameter. Specifies what the sliced image will have as a file name"


def main(argvs):
    opts = None
    try:
        # h - help, c - console based, t - img type, m - method (left or right), d - destination, s - source
        opts, args = getopt.getopt(argvs, 'hcs:d:t:m:n:')
    except getopt.GetoptError as e:
        print(e)
        exit(1)

    sourcedir = ""
    destinationdir = ""
    imgtype = None
    method = None
    filename = ""
    for opt, arg in opts:
        if opt == '-h':
            print('\n\n' + HELP + '\n')
            exit(0)
        elif opt == '-s':
            sourcedir = arg
        elif opt == '-d':
            destinationdir = arg
        elif opt == '-m':
            method = arg
        elif opt == '-t':
            imgtype = arg
        elif opt == '-n':
            filename = arg

    if imgtype is None:
        print("No image format provided")
        exit(1)
    if imgtype.lower() not in VALID_FORMATS:
        print("Invalid image format provided: " + imgtype)
        print("Type -h for command reference")
        exit(1)
    else:
        if method is None:
            print("No method provided.")
            exit(1)
        if method not in METHOD_KEY.keys():
            print("Invalid method provided")
            print("Type -h for command reference")
            exit(1)
        else:
            if filename == "":
                filename += "slicedimage"
                for i in range(5):
                    filename += chr(random.randint(48, 57))
            if imgtype.lower() == 'ppm':
                info = handleppm(filename, sourcedir, destinationdir, METHOD_KEY[method])
            else:
                info = handlegeneric(filename, sourcedir, destinationdir, imgtype, METHOD_KEY[method])
            print('Images have been sliced. Product can be found in {} under the name {}'.format
                  (info[0], filename + '.' + imgtype))
            print('\n')

if __name__ == '__main__':
    main(sys.argv[1:])
