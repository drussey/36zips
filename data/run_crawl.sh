#!/bin/bash
cd /home/dan/rap-kilo-index
SLEEP=2.5 SONGS=50 python3 data/annot_crawl.py 2>&1 | grep --line-buffered -E "^done|429|no artist|CRAWL DONE|Traceback|Error" >> data/pipeline.log
echo "$(date) CRAWL EXIT" >> data/pipeline.log
