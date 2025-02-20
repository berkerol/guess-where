import os
import subprocess

import boto3

from guess_where import FILE_EXTENSION, DOWNLOAD_PATH, list_files_in_disk, list_files_in_s3, process_s3_path, download_file_from_s3


def get_file_count(path):
    output = subprocess.check_output(f'find "{path}" -type f -name "*.{FILE_EXTENSION}" | wc -l', shell=True)
    return int(output.decode('utf-8'))


def test_list_files_in_disk_1():
    path = '/home/berk/Photos/'
    assert len(list_files_in_disk(path)) == int(get_file_count(path))


def test_list_files_in_disk_2():
    path = '/home/berk/Photos 2'
    assert len(list_files_in_disk(path)) == int(get_file_count(path))


def test_list_files_in_s3_1():
    path = '/home/berk/Photos/'
    assert len(list_files_in_s3('berkerol', 'Photos/')) == int(get_file_count(path))


def test_list_files_in_s3_2():
    path = '/home/berk/Photos 2/'
    assert len(list_files_in_s3('berkerol', 'Photos 2/')) == int(get_file_count(path))


def test_process_s3_path_1():
    path = '/home/berk/Photos/'
    assert len(process_s3_path('s3://berkerol/Photos/')[0]) == int(get_file_count(path))


def test_process_s3_path_2():
    path = '/home/berk/Photos 2/'
    assert len(process_s3_path('s3://berkerol/Photos 2/')[0]) == int(get_file_count(path))


def test_download_file_from_s3():
    path = DOWNLOAD_PATH + 'IMG_20180404_180516.jpg'
    s3_path = 's3://Photos/Bayern/München/IMG_20180404_180516.jpg'
    assert os.path.exists(path) is False
    assert download_file_from_s3(s3_path, boto3.resource('s3').Bucket('berkerol')) == path
    assert os.path.exists(path)
    os.remove(path)
