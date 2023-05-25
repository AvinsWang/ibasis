#!/bin/bash

pwd=$(pwd)
src_dir="ibasis"
dst_dir="ibasis_funcs"

# 创建目标目录
mkdir -p "$dst_dir"
cd "$dst_dir"

# 遍历 a/ 目录下的所有文件（除了 __init__.py）
for file in "../$src_dir"/*.py; do
    # 排除 __init__.py 文件
    if [[ $(basename "$file") != "__init__.py" ]]; then
        # 检查是否已经链接过
        if [ ! -e "$(basename "$file")" ]; then
            # 创建软链接到目标目录
            ln -s "$file" "."
        fi
    fi
done

cd "$pwd"

# 遍历目标目录中的所有 .py 文件py
for file in "$dst_dir"/*.py; do
    # 获取文件名（不包括路径和后缀）
    filename=$(basename "$file" .py)
    # 将 import 语句写入 __init__.py 文件
    echo "from .$filename import *" >> "$dst_dir/__init__.py"
done

version=$(grep -oP "version='\K[^']+" setup.py)

rm -rf build/ dist/ ibasis.egg-info/ && \
python setup.py sdist bdist_wheel && \
pip install --force-reinstall  "dist/ibasis-$version-py3-none-any.whl"

# twine upload dist/*