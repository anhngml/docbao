#!/bin/bash
rclone sync -v docbao:category ~/docbao/client/category
rclone copy -v docbao:collocation.txt ~/docbao/client
rclone copy -v docbao:stopwords-nlp-vi.txt ~/docbao/client
cd ~/docbao/client
python3.4 docbao.py
rclone copy -v ~/docbao/client/article_data.json docbao:
rclone copy -v ~/docbao/client/hot_keyword.json docbao:
rclone copy -v ~/docbao/client/keyword_dict.json docbao:
rclone copy -v ~/docbao/client/hot_keyword.json docbao:
rclone copy -v ~/docbao/client/log_data.json docbao:
rclone copy -v ~/docbao/client/uncategorized_keyword.txt docbao:
