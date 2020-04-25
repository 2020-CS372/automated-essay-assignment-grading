from plagiarism.data import plagiarism_data
from plagiarism.sync import plagiarism_sync
from quality.data import quality_data
from quality.sync import quality_sync


def data():
    quality_data()
    plagiarism_data()


def sync():
    quality_sync()
    plagiarism_sync()


def main():
    data()
    sync()


if __name__ == '__main__':
    main()
