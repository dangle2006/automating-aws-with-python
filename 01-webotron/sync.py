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
files = []


@click.command()
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket_name')
@click.option('--profile', default=None,
              help="Use a given AWS profile.")
def sync(pathname, bucket_name, profile):
    """Sync contents of PATHNAME to BUCKET."""

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

    print("Transfer Config - ", transfer_config)

    print("Contents of the bucket .. {} .. are as follows -".format(bucket_name))

    bucket = s3.Bucket(bucket_name)

    for obj in bucket.objects.all():
        print(obj)


    ## load_manifest(bucket)
    """Load manifest for caching purposes."""
    paginator = s3.meta.client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket.name):
        for obj in page.get('Contents', []):
            manifest[obj['Key']] = obj['ETag']
    print("manifest -:", manifest)


    root = Path(pathname).expanduser().resolve()
    global source_dir_abs
    source_dir_abs = Path(pathname).expanduser().resolve()
    print("Root  is ... {}".format(root))
    handle_directory(root)

    print("Files list in source ", files)

    




def handle_directory(root):
    for p in root.iterdir():
        if p.is_dir():
            print("Directory is ", p)
            handle_directory(p)
        if p.is_file():
            file_string = str(p.relative_to(source_dir_abs))
            files.append(file_string)
            print("Adding ... ", file_string)
            # upload_file(bucket, str(p), str(p.relative_to(root)))


def get_region_name(bucket):
    """Get the bucket's region name."""
    client = s3.meta.client
    bucket_location = client.get_bucket_location(Bucket=bucket.name)

    return bucket_location["LocationConstraint"] or 'us-east-1'


if __name__ == '__main__':
    print({})
    sync()





    #
    # bucket_url = "http://{}.{}".format(
    #                 bucket.name,
    #                 util.get_endpoint(get_region_name(bucket_name)).host
    #                 )
    #
    # print(bucket_url)
