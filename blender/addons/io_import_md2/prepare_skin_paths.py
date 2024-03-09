import os


def get_path_from_skin_name(md2_path: str, skin_name: str):
    # strings are always stored as 64 bytes, so unused bytes are set to '\x00'
    first_stored_path = skin_name.rstrip("\x00")
    # only first stored path is used since Digital Paintball 2 only uses that one
    first_stored_path = first_stored_path.split("/")[-1]
    print(f'first_stored_path: {first_stored_path}')
    # absolute path is formed by using the given md2 object path
    absolute_first_stored_path = "/".join(md2_path.split("/")[:-1]) + "/" + first_stored_path
    print(f'absolute_first_stored_path: {absolute_first_stored_path}')
    skin_path = absolute_first_stored_path

    return skin_path


def get_existing_skin_path(skin_path: str):
    """
    Replaces the skin path extension with the one of an existing file of the same name.
    """
    """ Look for existing file of given name and supported image format """
    supported_image_formats = [".png", ".jpg", ".jpeg", ".tga", ".pcx"]  # Order doesn't match DP2 image order
    skin_path_unextended = os.path.splitext(skin_path)[0]  # remove extension (last one)
    print(f'skin_path_unextended: {skin_path_unextended}')
    for format in supported_image_formats:
        full_path = skin_path_unextended + format
        print(f'full_path: {full_path}')
        if os.path.isfile(full_path):
            skin_path = skin_path_unextended + format
            return skin_path
