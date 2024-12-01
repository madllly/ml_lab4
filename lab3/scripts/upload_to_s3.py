import argparse
import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()


def create_bucket(bucket_name):
    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
        aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
    )
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    except ClientError as e:
        print(f"Failed to create bucket '{bucket_name}': {e}")


def upload_file_to_s3(bucket, file_path):
    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
        aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
    )

    object_name = file_path.split("/")[-1]
    s3.upload_file(file_path, bucket, object_name)
    print(f"File '{object_name}' uploaded to bucket '{bucket}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to S3 and create bucket if needed")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--file_path", required=True, help="File path to upload")
    parser.add_argument(
        "--create_bucket", action="store_true", help="Create the bucket if it does not exist"
    )
    args = parser.parse_args()

    if args.create_bucket:
        create_bucket(args.bucket)

    upload_file_to_s3(args.bucket, args.file_path)
