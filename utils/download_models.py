# download_script.py
import argparse
import os
import dotenv
from pathlib import Path
from huggingface_hub import snapshot_download, login

ROOT = Path(__file__).parent.parent
dotenv.load_dotenv(ROOT / ".env")

HF_KEY = os.getenv("HF_KEY")
login(token=HF_KEY)


def download_model(model_full_name: str, model_folder_name: str, local_dir: str = None):
    """
    Downloads a Hugging Face model snapshot to a specified local directory.
    """
    
    # Construct the final local directory path
    if local_dir:
        # If local_dir is provided, we use it directly or combine with model_folder_name
        final_local_dir = os.path.join(local_dir, model_folder_name)
    else:
        # Default to a relative cache directory if local_dir is not provided
        final_local_dir = os.path.join("..", ".cache", model_folder_name)
        
    print(f"Starting download for {model_full_name}...")
    print(f"Target directory: {final_local_dir}")

    # Perform the download
    model_path = snapshot_download(
        repo_id=model_full_name,
        local_dir=final_local_dir,
        # Set resume_download=True for robust downloading
        resume_download=True 
    )

    print(f"\n✅ Model {model_full_name} successfully downloaded to: {model_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a Hugging Face model using command-line arguments."
    )
    
    # Required Arguments
    parser.add_argument(
        "model_full_name",
        type=str,
        help="The full Hugging Face model repository ID (e.g., Qwen/Qwen3-4B-Instruct-2507)"
    )
    parser.add_argument(
        "model_folder_name",
        type=str,
        help="The local folder name for the model (e.g., Qwen3-4B)"
    )
    
    # Optional Argument
    parser.add_argument(
        "--local_dir",
        type=str,
        default=None,
        help="The root directory where the model cache will be created (e.g., ./my_models). If omitted, it defaults to ../.cache."
    )

    args = parser.parse_args()
    
    # Call the download function with parsed arguments
    download_model(
        model_full_name=args.model_full_name,
        model_folder_name=args.model_folder_name,
        local_dir=args.local_dir
    )
