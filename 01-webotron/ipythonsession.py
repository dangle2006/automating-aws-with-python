# coding: utf-8
import boto3
from pathlib import Path
import os

session = boto3.Session(profile_name='pythonAutomation')
s3 = session.resource('s3')


bucket_name = "danana2379"
pathname = "kitten_web"

bucket = s3.Bucket(bucket_name)

dest_files = []
files = []

for obj in bucket.objects.all():
    dest_files.append(obj.key)
    print(obj.key)


root = Path(pathname).expanduser().resolve()
source_dir_abs = Path(pathname).expanduser().resolve()

print("Root  is ... {}".format(pathname))

source_files = []

for p in root.iterdir():
    if p.is_dir():
        print("Directory is ", p)
        for q in p.iterdir():
            if q.is_dir():
                print("Directory is ", q)
            if q.is_file():
                file_string = str(q.relative_to(source_dir_abs))
                source_files.append(file_string)
                print("Adding ... ", file_string)

    if p.is_file():
        file_string = str(p.relative_to(source_dir_abs))
        source_files.append(file_string)

        print("Adding ... ", file_string)


x = len(source_files) - 1
while x+1  > 0 :
    if dest_files[x] in source_files:
        print('\x1b[6;30;42m' + "File {} exists".format(fil) + '\x1b[0m')
    else:
        print(x)
        print("File {} doesn't exist".format(fil))
        dest_files.pop(x)
    x -= 1
