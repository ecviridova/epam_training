import filecmp
import hashlib
import os
import sys


def hash_value(filename):
    with open(filename, "rb") as f:
        bytes = f.read()  # read file as bytes
    return hashlib.md5(bytes).hexdigest()


def are_file_contents_equal(filename1, filename2):
    """Determine if the contents of two files are equal"""
    return filecmp.cmp(filename1, filename2, shallow=False)


def is_already_hardlinked(filename1, filename2):
    result = (os.stat(filename1).st_ino == os.stat(filename2).st_ino)  # Inodes equal
    return result


def eligible_for_hardlink(filename1,
                          filename2,
                          ):
    result = (
        # Must meet the following
        # criteria:
            not is_already_hardlinked(filename1, filename2) and           # NOT already hard linked

            are_file_contents_equal(filename1, filename2) and             # file contents are equal

            os.stat(filename1).st_size == os.stat(filename1).st_size and  # size is the same

            os.stat(filename1).st_size != 0 and                           # size is not zero

            os.stat(filename1).st_mode == os.stat(filename2).st_mode and

            os.stat(filename1).st_dev == os.stat(filename1).st_dev        # device is the same

    )
    if None:
        # if not result:
        print("Already hardlinked: %s" % (not is_already_hardlinked(filename1, filename2)))
    return result


# Hardlink two files together

def hardlink_files(sourcefile, destfile):
    # rename the destination file to save it
    temp_name = destfile + ".$$$___cleanit___$$$"
    try:
        os.rename(destfile, temp_name)
    except OSError:
        error = sys.exc_info()[1]
        print("Failed to rename: %s to %s: %s" % (destfile, temp_name, error))
        result = False
    else:
        # Now link the sourcefile to the destination file
        try:
            os.link(sourcefile, destfile)
        except Exception:
            error = sys.exc_info()[1]
            print("Failed to hardlink: %s to %s: %s" % (sourcefile, destfile, error))
            # Try to recover
            try:
                os.rename(temp_name, destfile)
            except Exception:
                error = sys.exc_info()[1]
                print("BAD - failed to rename back %s to %s: %s" % (temp_name, destfile, error))
            result = False
        else:
            # hard link succeeded
            # Delete the renamed version since we don't need it.
            os.unlink(temp_name)
            # update our stats
            result = True
    return result


def hardlink_identical_files(directory):
    for filename in os.listdir(directory):
        filename = os.path.normpath(os.path.join(directory, filename))
        if os.path.isfile(filename):

            filehash = hash_value(filename)
            if filehash in file_hashes:
                # We have file(s) that have the same hash as our current file.
                # Let's go through the list of files with the same hash and see if
                # we are already hardlinked to any of them.
                for unique_file in file_hashes.keys():
                    if is_already_hardlinked(filename, unique_file):
                        break
                    elif eligible_for_hardlink(filename, unique_file):
                        hardlink_files(filename, unique_file)
                        print(filename + " is hardlinked")
                    else:
                        file_hashes[filename].append(filehash)
            else:
                file_hashes[filename] = filehash


# Global

file_hashes = None


def main(directory):
    global file_hashes

    file_hashes = {}

    # try:
    dir_entries = os.listdir(directory)
    # except OSError:
    #     print("Error: Unable to do an os.listdir on: %s  Skipping..." % directory)

    for entry in dir_entries:
        pathname = os.path.normpath(os.path.join(directory, entry))
        print(pathname)
        if os.path.islink(pathname):
            print("%s: is a symbolic link, ignoring" % pathname)
        if os.path.isdir(pathname):
            print("%s is a directory!" % pathname)

        hardlink_identical_files(directory)


if __name__ == '__main__':
    main("/home/kate/testfolder")
