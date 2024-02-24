# !/bin/bash
if [ -d $data/models/models--TencentARC--PhotoMaker ];
then
    echo "Model pre-installed"
else
    python3 -c 'import os; os.environ["HF_HOME"] = "../data/models"; os.environ["TRANSFORMERS_CACHE"] = "../data/models"; from huggingface_hub import hf_hub_download; downloaded_model_path = hf_hub_download(repo_id="TencentARC/PhotoMaker",filename="photomaker-v1.bin",repo_type="model",cache_dir="../data/models"); print(downloaded_model_path)'
fi