import shutil
import sys
def download_all_files_from_bucket(bucket_name, output_dir):
    s3 = get_s3_client()
    os.makedirs(output_dir, exist_ok=True)
    print(f"Checking files in bucket '{bucket_name}' to download to '{output_dir}'...")
    try:
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                key = obj['Key']
                dest_path = os.path.join(output_dir, key)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                while True:
                    resp = input(f"Download '{key}' to '{dest_path}'? [y/n/q]: ").strip().lower()
                    if resp == 'y':
                        print(f"Downloading {key} -> {dest_path}")
                        with open(dest_path, 'wb') as f:
                            s3.download_fileobj(bucket_name, key, f)
                        break
                    elif resp == 'n':
                        print(f"Skipping {key}")
                        break
                    elif resp == 'q':
                        print("Quitting download loop.")
                        return
                    else:
                        print("Please enter 'y' to download, 'n' to skip, or 'q' to quit.")
    except Exception as e:
        print(f"Error downloading files: {e}")

import boto3
import os
import subprocess
import yaml

import getpass
import tempfile

# Decrypt the Ansible Vault file and load credentials
def load_vault_credentials(vault_path):
    password = getpass.getpass("Ansible Vault password: ")
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as pwfile:
        pwfile.write(password + "\n")
        pwfile.flush()
        pwfile_name = pwfile.name
    try:
        result = subprocess.run([
            "ansible-vault", "view", vault_path, "--vault-password-file", pwfile_name
        ], capture_output=True, text=True, check=True)
        data = yaml.safe_load(result.stdout)
        return data
    except subprocess.CalledProcessError as e:
        print("Failed to decrypt vault file:", e.stderr)
        exit(1)
    finally:
        os.remove(pwfile_name)

vault_file = os.path.join(os.path.dirname(__file__), "ansible-vault.yml")

creds = load_vault_credentials(vault_file)
if not isinstance(creds, dict):
    print(f"ERROR: Vault file did not parse as a dictionary. Type: {type(creds)}. Content: {creds}")
    exit(1)

def get_cred(key, creds):
    if key not in creds:
        print(f"ERROR: '{key}' not found in vault credentials. Available keys: {list(creds.keys())}")
        exit(1)
    value = creds[key]
    # Remove quotes if present (handles YAML like KEY:"value")
    if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    return value

os.environ["AWS_ACCESS_KEY_ID"] = get_cred("AWS_ACCESS_KEY_ID", creds)
os.environ["AWS_SECRET_ACCESS_KEY"] = get_cred("AWS_SECRET_ACCESS_KEY", creds)
if "AWS_SESSION_TOKEN" in creds:
    os.environ["AWS_SESSION_TOKEN"] = get_cred("AWS_SESSION_TOKEN", creds)
if "AWS_ENDPOINT" in creds:
    os.environ["AWS_ENDPOINT"] = get_cred("AWS_ENDPOINT", creds)
# AWS_BUCKET is available in creds["AWS_BUCKET"] for later use


def get_s3_client():
    endpoint_url = os.environ.get("AWS_ENDPOINT")
    if endpoint_url:
        return boto3.client('s3', endpoint_url=endpoint_url)
    return boto3.client('s3')

def list_s3_buckets():
    s3 = get_s3_client()
    response = s3.list_buckets()
    print("Buckets in your account:")
    for bucket in response['Buckets']:
        print(f"- {bucket['Name']}")

def list_files_in_bucket(bucket_name):
    s3 = get_s3_client()
    print(f"Files in bucket '{bucket_name}':")
    try:
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                print(f"- {obj['Key']}")
    except Exception as e:
        print(f"Error listing files: {e}")

if __name__ == "__main__":
    list_s3_buckets()
    if "AWS_BUCKET_NAME" in creds:
        bucket_name = get_cred("AWS_BUCKET_NAME", creds)
        list_files_in_bucket(bucket_name)
        download_all_files_from_bucket(bucket_name, "output")
