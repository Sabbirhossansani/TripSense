"""
One-command deployer for TripSense FastAPI + PyTorch backend to Hugging Face Spaces
(Free Tier: CPU Basic • 2 vCPUs • 16 GB RAM).

Usage:
  1. Ensure your .env has a Hugging Face token with WRITE access:
     HF_WRITE_TOKEN=hf_... (or set HF_TOKEN to a write-scoped token)
  2. Run:
     python scripts/deploy_hf_space.py --space tripsense-api
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from huggingface_hub import HfApi

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))


def main():
    parser = argparse.ArgumentParser(description="Deploy TripSense API to Hugging Face Spaces (Docker SDK)")
    parser.add_argument("--space", default="tripsense-api", help="Target Space name (default: tripsense-api)")
    args = parser.parse_args()

    token = (os.getenv("HF_WRITE_TOKEN") or os.getenv("HF_TOKEN") or "").strip()
    if not token:
        print("ERROR: Missing HF_WRITE_TOKEN or HF_TOKEN in environment / .env.")
        sys.exit(1)

    api = HfApi(token=token)
    info = api.whoami()
    username = info.get("name")
    role = info.get("auth", {}).get("accessToken", {}).get("role", "unknown")
    print(f"[HF Deploy] Authenticated as '{username}' (token role: {role})")

    if role == "read":
        print(
            "\nERROR: Your current HF token only has 'read' permission.\n"
            "Create a 'Write' token at https://huggingface.co/settings/tokens, add HF_WRITE_TOKEN=hf_... to .env,\n"
            "and re-run: python scripts/deploy_hf_space.py"
        )
        sys.exit(2)

    repo_id = f"{username}/{args.space}"
    print(f"[HF Deploy] Creating/updating public Docker Space: {repo_id}")
    api.create_repo(
        repo_id=repo_id,
        repo_type="space",
        space_sdk="docker",
        private=False,
        exist_ok=True,
    )

    api.upload_file(
        path_or_fileobj=os.path.join(ROOT_DIR, "hf_space", "README.md"),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="space",
    )
    api.upload_file(
        path_or_fileobj=os.path.join(ROOT_DIR, "Dockerfile"),
        path_in_repo="Dockerfile",
        repo_id=repo_id,
        repo_type="space",
    )
    api.upload_folder(
        folder_path=os.path.join(ROOT_DIR, "backend"),
        path_in_repo="backend",
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=["ml/data_cache/**", "**/__pycache__/**", "*.pyc"],
    )
    dist_dir = os.path.join(ROOT_DIR, "frontend", "dist")
    if os.path.exists(dist_dir):
        api.upload_folder(
            folder_path=dist_dir,
            path_in_repo="frontend/dist",
            repo_id=repo_id,
            repo_type="space",
        )

    space_url = f"https://{username.lower()}-{args.space.lower()}.hf.space"
    print(f"\nSUCCESS! Space pushed to Hugging Face:")
    print(f"  Dashboard : https://huggingface.co/spaces/{repo_id}")
    print(f"  Direct API: {space_url}")
    print(f"  Health URL: {space_url}/health")


if __name__ == "__main__":
    main()
