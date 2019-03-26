#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Standalone test to run the sync & also delete sync"""

from pathlib import Path

import boto3
import click
import webotron.util

session = None
bucket_manager = None

CHUNK_SIZE = 8388608
source_files = []


@click.command()
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket_name')
@click.option('--profile', default=None,
              help="Use a given AWS profile.")
@click.option('--delete', is_flag=True, help='Delete files that arent in the source.')

def sync(pathname, bucket_name, profile, delete):
    """Sync contents of PATHNAME to BUCKET."""
    if delete:
        print("--delete SELECTED")
        global session

    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile
    session = boto3.Session(**session_cfg)
    s3 = session.resource('s3')

    transfer_config = boto3.s3.transfer.TransferConfig(
        multipart_chunksize = CHUNK_SIZE,
        multipart_threshold = CHUNK_SIZE
    )
    manifest = {}

    print("Contents of the bucket .. {} .. are as follows -".format(bucket_name))
    bucket = s3.Bucket(bucket_name)
    dest_files = []
    for obj in bucket.objects.all():
        dest_files.append(obj.key)
        print("A dest_file", obj.key)

    ## load_manifest(bucket)
    """Load manifest for caching purposes."""
    paginator = s3.meta.client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket.name):
        for obj in page.get('Contents', []):
            manifest[obj['Key']] = obj['ETag']

    root = Path(pathname).expanduser().resolve()

    source_dir_abs = Path(pathname).expanduser().resolve()
    handle_directory(root, source_dir_abs)

    if delete:
        files_to_delete = []
        print("\n","Dest files ....", dest_files)
        x = len(dest_files) - 1
        while x+1  > 0 :
            if dest_files[x] in source_files:
                print('\x1b[6;30;42m' + "File {} exists".format(dest_files[x]) + '\x1b[0m')
            else:
                print("File {} doesn't exist on source".format(dest_files[x]))
                files_to_delete.append(dest_files[x])
            x -= 1

        for f in files_to_delete:
            delete_file(s3, bucket_name, f)
            print("Deleting .... ", f)

    for file in source_files:
        upload_file(bucket, file)


def handle_directory(root, source_dir_abs):
    for p in root.iterdir():
        if p.is_dir():
            handle_directory(p, source_dir_abs)
        if p.is_file():
            file_string = str(p.relative_to(source_dir_abs))
            source_files.append(file_string)

def delete_file(s3, bucket_name, file_string):
    obj = s3.Object(bucket_name, file_string)
    obj.delete()

def upload_file(bucket_name, file):
    print("Uploading ...", file)

def get_region_name(bucket):
    """Get the bucket's region name."""
    client = s3.meta.client
    bucket_location = client.get_bucket_location(Bucket=bucket.name)

    return bucket_location["LocationConstraint"] or 'us-east-1'


if __name__ == '__main__':
    # print({})
    sync()





    #
    # bucket_url = "http://{}.{}".format(
    #                 bucket.name,
    #                 util.get_endpoint(get_region_name(bucket_name)).host
    #                 )
    #
    # print(bucket_url)
