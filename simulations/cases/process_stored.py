from os import listdir
from os.path import isfile, join


def process(directory: str):
    files = [f for f in listdir(directory) if isfile(join(directory, f))]


if __name__ == '__main__':
    process('../../../simulation-results')
