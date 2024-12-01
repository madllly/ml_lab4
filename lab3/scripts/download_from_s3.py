import argparse
import os

import boto3
from dotenv import load_dotenv

load_dotenv()


def download_file_from_s3(bucket, object_name, download_path):
    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
        aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
    )
    with open(download_path, "wb") as f:
        s3.download_fileobj(bucket, object_name, f)
    print(f"File {object_name} downloaded from {bucket} to {download_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download file from S3 bucket")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--object_name", required=True, help="S3 object name")
    parser.add_argument("--download_path", required=True, help="Path to save the downloaded file")
    args = parser.parse_args()

    download_file_from_s3(args.bucket, args.object_name, args.download_path)
