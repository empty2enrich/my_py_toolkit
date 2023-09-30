
from huggingface_hub import snapshot_download#, hf_hub_url, hf_hub_download, get_hf_file_metadata

# download
snapshot_download(repo_id="bert-base-multilingual-cased", cache_dir='./bert-base-multilingual-cased')