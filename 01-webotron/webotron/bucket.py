# -*- coding: utf-8 -*-

"""Classes for S3 Buckets."""

from pathlib import Path
import mimetypes

from botocore.exceptions import ClientError


class BucketManager:
    """Manage an S3 Bucket."""

    def __init__(self, session):
        """Create a BucketManager object."""
        self.session = session
        self.s3 = self.session.resource('s3')

    def all_buckets(self):
        """Get an iterator for all buckets."""
        return self.s3.buckets.all()

    def all_objects(self, bucket):
        """Get an iterator for all objects in the bucket."""
        return self.s3.Bucket(bucket).all_objects

    def init_bucket(self, bucket):
        """Create a new S3 web bucket."""
        s3_bucket = None
        try:
            s3_bucket = self.s3.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={
                    'LocationConstraint': self.session.region_name
                }
            )
        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket)
            else:
                raise error

        return s3_bucket

    @staticmethod
    def set_policy(bucket):
        """Set bucket policy to be readable by everyone."""
        policy = """
        {
          "Version":"2012-10-17",
          "Statement":[{
          "Sid":"PublicReadGetObject",
          "Effect":"Allow",
          "Principal": "*",
              "Action":["s3:GetObject"],
              "Resource":["arn:aws:s3:::%s/*"
              ]
            }
          ]
        }
        """ % bucket.name
        policy = policy.strip()

        print("bucket variable :", bucket, "  ", bucket.name)

        pol = bucket.Policy()
        pol.put(Policy=policy)

    @staticmethod
    def configure_website(bucket):
        """S3 website config for bucket."""
        bucket.Website().put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        })

    @staticmethod
    def upload_file(bucket, path, key):
        """Upload path to s3_bucket at key."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'

        bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            })

    def sync(self, pathname, bucket_name):
        """Sync files to the S3 bucket."""
        bucket = self.s3.Bucket(bucket_name)
        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    self.upload_file(bucket, str(p), str(p.relative_to(root)))

        handle_directory(root)
