import argparse
import os

import boto3
from botocore.exceptions import ClientError


def upload_files_to_s3(bucket, directory):
    s3 = boto3.client(
        "s3",
        endpoint_url=f"http://{os.getenv('MINIO_ENDPOINT')}",
        aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
        aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
    )

    # Проверяем, существует ли bucket
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            s3.create_bucket(Bucket=bucket)
            print(f"Bucket '{bucket}' created.")
        else:
            print(f"Error accessing bucket '{bucket}': {e}")
            raise

    # Загружаем файлы и создаем директории
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            dir_path = os.path.relpath(os.path.join(root, dir_name), directory) + "/"
            try:
                s3.put_object(Bucket=bucket, Key=dir_path)
                print(f"Created directory {dir_path} in bucket {bucket}.")
            except ClientError as e:
                print(f"Failed to create directory {dir_path}: {e}")

        for file in files:
            file_path = os.path.join(root, file)
            object_name = os.path.relpath(file_path, directory)
            try:
                s3.upload_file(file_path, bucket, object_name)
                print(f"Uploaded {file_path} to bucket {bucket} as {object_name}.")
            except ClientError as e:
                print(f"Failed to upload {file_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", type=str, required=True, help="S3 bucket name.")
    parser.add_argument(
        "--directory", type=str, required=True, help="Directory with experiment results."
    )
    args = parser.parse_args()

    upload_files_to_s3(args.bucket, args.directory)
