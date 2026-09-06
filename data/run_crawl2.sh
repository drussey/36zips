#!/bin/bash
cd /home/dan/rap-kilo-index
ROSTER=data/artists_followup.txt SLEEP=2.5 SONGS=50 python3 data/annot_crawl.py 2>&1 | grep --line-buffered -E "^done|429|no artist|CRAWL DONE|Traceback|Error" >> data/pipeline.log
echo "$(date) CRAWL2 EXIT" >> data/pipeline.log
