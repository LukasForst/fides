from os import listdir

from fides.model.configuration import TrustModelConfiguration, load_configuration


def find_config(file_name: str = 'fides.conf.yml') -> TrustModelConfiguration:
    """Loads configuration from the root of the repository.

    Tries to find the correct file in python path.
    """
    prev = None
    curr = '.'
    final_path = None
    while True:
        folder_content = listdir(curr)
        if file_name in folder_content:
            # file was found, so we set it and drop the last '.'
            final_path = curr[:len(curr) - 1] + file_name
            break
        if folder_content == prev:
            # if the current folder is same as the previous one we need to break
            break
        prev = folder_content
        curr = f'../{curr}'

    if final_path is None:
        raise Exception(f'Config file {file_name} not found!')
    else:
        return load_configuration(file_path=final_path)
