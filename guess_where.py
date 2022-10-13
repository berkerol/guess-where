import boto3

import argparse
import os
import pwd
import random
import subprocess
import time

S3_PREFIX = 's3://'
FILE_EXTENSION = 'jpg'
DOWNLOAD_PATH = f'/home/{pwd.getpwuid(os.getuid())[0]}/Pictures/Guess Where/'


def get_guess_name(file_name):
    file_name_components = file_name.split('/')
    first_dir_name = file_name_components[0]
    # format: date - order - country - city/**/jpg
    if ' - ' in first_dir_name:
        first_dir_name_components = first_dir_name.split(' - ')
        return first_dir_name_components[-1]
    # format: country/city/**/jpg
    return file_name_components[1]


def list_files_in_disk(path):
    file_dict = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            file_name = os.path.join(root, file)
            if file_name.endswith(FILE_EXTENSION):
                # remove directories in search path to get first contextful dir
                short_name = file_name[(len(path) + 1):]
                file_dict[file_name] = get_guess_name(short_name)

    return file_dict


def list_files_in_s3(bucket, prefix):
    s3 = boto3.client('s3')

    file_dict = {}
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    while True:
        for obj in response['Contents']:
            file_name = obj['Key']
            if file_name.endswith(FILE_EXTENSION):
                # remove first directory to get first contextful directory
                short_name = file_name[(file_name.find('/') + 1):]
                # put s3 prefix to understand if we need to download the file
                file_dict[S3_PREFIX + file_name] = get_guess_name(short_name)
        if 'NextContinuationToken' in response:
            token = response['NextContinuationToken']
            response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix,
                                          ContinuationToken=token)
        else:
            break

    return file_dict


def process_s3_path(path):
    # remove s3 prefix
    path = path[len(S3_PREFIX):]
    if '/' in path:  # format: bucket/prefix/
        slash_index = path.find('/')
        bucket = path[:slash_index]
        prefix = path[(slash_index + 1):]
    else:  # format: bucket
        bucket = path
        prefix = ''
    file_dict = list_files_in_s3(bucket, prefix)
    s3 = boto3.resource('s3').Bucket(bucket)
    # create the download path if it doesn't exist
    subprocess.run(['mkdir', '-p', DOWNLOAD_PATH])
    return file_dict, s3


def download_file_from_s3(file_name, s3):
    # remove s3 prefix
    obj = file_name[len(S3_PREFIX):]
    # add file name to download path
    download_path = DOWNLOAD_PATH + obj.split('/')[-1]
    s3.download_file(obj, download_path)
    return download_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='absolute or relative path \
                                      or s3 path like s3://bucket/prefix/')
    parser.add_argument('-w', '--watch', default=5, type=int,
                        help='time period to view the photo')
    parser.add_argument('-s', '--sleep', default=2, type=int,
                        help='time period to see the result')
    args = parser.parse_args()

    if not args.path.startswith(S3_PREFIX):
        file_dict = list_files_in_disk(args.path)
    else:
        file_dict, s3 = process_s3_path(args.path)

    file_list = list(file_dict.items())
    correct_guesses, false_guesses, current_streak, highest_streak = 0, 0, 0, 0

    while True:
        random_file = random.choice(file_list)

        file_name = random_file[0]
        # download file first to give it as input to shotwell
        if file_name.startswith(S3_PREFIX):
            file_name = download_file_from_s3(file_name, s3)

        process = subprocess.Popen(['shotwell', '-f', file_name])
        time.sleep(args.watch)
        process.kill()

        try:
            guess = input('Guess: ')
        except UnicodeDecodeError:
            # fail silently, invalid char will be wrong answer anyway
            guess = ''
        except (EOFError, KeyboardInterrupt):
            break  # exit

        if guess.lower() in random_file[1].lower():
            print('Correct')
            correct_guesses += 1
            current_streak += 1
        else:
            print('No, it was ' + random_file[1])
            false_guesses += 1
            if current_streak > highest_streak:
                highest_streak = current_streak
                print(f'Highest streak ended with {highest_streak}')
            elif current_streak > 0:
                print(f'Streak ended with {current_streak}')
            current_streak = 0

        time.sleep(args.sleep)

    total_guesses = correct_guesses + false_guesses
    print(f'\nCorrect guesses: {correct_guesses}/{total_guesses}')

    if current_streak > highest_streak:
        highest_streak = current_streak
    print(f'Highest streak: {highest_streak}')
