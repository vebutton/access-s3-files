# Access S3 Files

A Python script to list and download files from any S3-compatible bucket (e.g., AWS S3, Backblaze B2) using credentials stored securely in an Ansible Vault-encrypted YAML file.

## Features
- Lists all buckets and files in a specified bucket
- Downloads files from the bucket to a local directory, with per-file confirmation
- Supports custom S3 endpoints (for non-AWS providers)
- Credentials are never stored in code or .env files

## Setup

1. **Clone the repository:**
	```sh
	git clone https://github.com/vebutton/access-s3-files.git
	cd access-s3-files
	```

2. **Create and activate a virtual environment (recommended):**
	```sh
	python3 -m venv .venv
	source .venv/bin/activate
	```

3. **Install dependencies:**
	```sh
	pip install boto3 pyyaml
	```

4. **Prepare your vault file:**
	- Copy `ansible-vault.yml.example` to `ansible-vault.yml` and fill in your real credentials.
	- Encrypt it with Ansible Vault:
	  ```sh
	  ansible-vault encrypt ansible-vault.yml
	  ```

	Example YAML structure:
	```yaml
	AWS_ACCESS_KEY_ID: your_access_key
	AWS_SECRET_ACCESS_KEY: your_secret_key
	AWS_ENDPOINT: https://your-s3-endpoint
	AWS_BUCKET_NAME: your-bucket
	```

5. **Run the script:**
	```sh
	python access_s3_bucket.py
	```
	You will be prompted for your Ansible Vault password and for each file to download.

## Security
- Never commit your real `ansible-vault.yml` to version control.
- Only share the `.example` file for reference.

## License
MIT
