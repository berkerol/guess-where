import boto3

from PIL import ImageTk, Image

import os
import pwd
import random
import subprocess
import sys

from tkinter import Tk, ttk, Toplevel, filedialog, IntVar, StringVar

S3_PREFIX = 's3://'
FILE_EXTENSION = 'jpg'
HOME_PATH = f'/home/{pwd.getpwuid(os.getuid())[0]}/'
DOWNLOAD_PATH = f'{HOME_PATH}Pictures/Guess Where/'


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
    s3 = None
    file_list = []
    random_file = ('', '')
    correct_guesses, total_guesses, current_streak, highest_streak = 0, 0, 0, 0

    root = Tk()
    root.title('Guess Where')
    root.attributes('-zoomed', True)
    root.resizable(False, False)
    watch_time, sleep_time, s3_path = IntVar(value=5), IntVar(value=2), StringVar(value='s3://')
    status_text, score_text, streak_text = StringVar(), StringVar(), StringVar()

    def update_score_and_streak_text():
        global score_text, streak_text
        score_text.set(f'Correct/Total guesses: {correct_guesses}/{total_guesses}')
        streak_text.set(f'Current/Highest streak: {current_streak}/{highest_streak}')

    update_score_and_streak_text()

    if len(sys.argv) > 1:  # for local testing
        file_list = list(list_files_in_disk(sys.argv[1]).items())
    else:
        window_choose = Toplevel(root)
        window_choose.title('Choose Photo Source - Guess Where')

        frame_choose = ttk.Frame(window_choose)
        frame_choose.grid(column=0, row=0, sticky='EW')

        def dismiss():
            window_choose.grab_release()
            window_choose.destroy()

        def choose_local_directory():
            global file_list
            path = filedialog.askdirectory(initialdir=HOME_PATH)
            file_dict = list_files_in_disk(path)
            file_list = list(file_dict.items())
            dismiss()

        def choose_s3_path():
            global s3, file_list
            file_dict, s3 = process_s3_path(s3_path.get())
            file_list = list(file_dict.items())
            dismiss()

        ttk.Label(frame_choose, text='Watch time').grid(column=0, row=0)
        ttk.Spinbox(frame_choose, from_=1, to=60, textvariable=watch_time).grid(column=1, row=0)
        ttk.Label(frame_choose, text='Sleep time').grid(column=0, row=1)
        ttk.Spinbox(frame_choose, from_=1, to=60, textvariable=sleep_time).grid(column=1, row=1)
        ttk.Button(frame_choose, text='Choose Local Directory', command=choose_local_directory)\
            .grid(column=0, row=2, columnspan=2)
        ttk.Entry(frame_choose, textvariable=s3_path).grid(column=0, row=3)
        ttk.Button(frame_choose, text='Use S3 Path', command=choose_s3_path).grid(column=1, row=3)
        frame_choose.grid_columnconfigure((0, 1), weight=1)

        window_choose.protocol('WM_DELETE_WINDOW', dismiss)
        window_choose.transient(root)
        window_choose.wait_visibility()
        window_choose.grab_set()
        window_choose.wait_window()

    frame_info = ttk.Frame(root)
    frame_info.grid(column=0, row=0, sticky='EW')

    def guess(event=None):
        global correct_guesses, total_guesses, current_streak, highest_streak
        guess = entry_guess.get().lower()
        entry_guess.delete(0, 'end')
        total_guesses += 1
        if guess == random_file[1].lower() or guess in random_file[1].lower().split(' '):
            status_text.set('Correct')
            correct_guesses += 1
            current_streak += 1
        else:
            status_text.set('No, it was ' + random_file[1])
            if current_streak > highest_streak:
                highest_streak = current_streak
                status_text.set(f'{status_text.get()}. Highest streak ended with {highest_streak}')
            elif current_streak > 0:
                status_text.set(f'{status_text.get()}. Streak ended with {current_streak}')
            current_streak = 0
        update_score_and_streak_text()
        root.after(sleep_time.get() * 1000, change_photo)

    root.bind('<Return>', guess)
    frame_guess = ttk.Frame(frame_info)
    frame_guess.grid(column=0, row=0, sticky='EW')
    entry_guess = ttk.Entry(frame_guess)
    entry_guess.grid(column=0, row=0)
    entry_guess.focus()
    ttk.Button(frame_guess, text='Guess', command=guess).grid(column=1, row=0)
    frame_guess.grid_columnconfigure((0, 1), weight=1)
    ttk.Label(frame_info, textvariable=status_text, anchor='center').grid(column=1, row=0)
    ttk.Label(frame_info, textvariable=score_text, anchor='center').grid(column=2, row=0)
    ttk.Label(frame_info, textvariable=streak_text, anchor='center').grid(column=3, row=0)
    frame_info.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform='label')
    root.update()
    frame_info.update()
    photo_height = root.winfo_height() - frame_info.winfo_height() - 2
    photo_width = int(photo_height / 9 * 16)

    frame_photo = ttk.Frame(root)
    frame_photo.grid(column=0, row=1)

    def set_photo(image):
        image_photo = ImageTk.PhotoImage(image)
        label_photo.configure(image=image_photo)
        label_photo.image = image_photo

    def change_photo():
        global random_file
        random_file = random.choice(file_list)
        file_name = random_file[0]
        # download file first to give it as input
        if file_name.startswith(S3_PREFIX):
            file_name = download_file_from_s3(file_name, s3)
        set_photo(Image.open(file_name).copy().resize((photo_width, photo_height)))
        status_text.set('')
        label_photo.after(watch_time.get() * 1000, lambda: set_photo(placeholder_image))

    label_photo = ttk.Label(frame_photo)
    label_photo.grid()
    placeholder_image = Image.new('RGBA', (photo_width, photo_height), (255, 0, 0, 0))
    change_photo()

    root.mainloop()
