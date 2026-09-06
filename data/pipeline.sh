#!/bin/bash
cd /home/dan/rap-kilo-index
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
echo "$(date) waiting for genius" 
until [ "$(curl -s -o /dev/null -w '%{http_code}' -A "$UA" 'https://genius.com/api/search/lyric?q=thirty%20for%20a%20brick&per_page=5')" = "200" ]; do sleep 120; done
echo "$(date) genius back; retry sweep"
python3 data/genius_sweep.py data/queries2_retry.txt data/raw_hits_3.json > data/sweep3.log 2>&1
echo "$(date) SWEEP DONE $(tail -1 data/sweep3.log)"
echo "$(date) annotation crawl"
python3 data/annot_crawl.py 2>&1 | grep --line-buffered -E "^done|429|no artist|CRAWL DONE|Traceback|Error"
echo "$(date) CRAWL EXIT"
