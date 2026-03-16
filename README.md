# ratelimit
Rate-limit command execution or stdin line throughput.
```bash
cat urls.txt | python ratelimit.py lines -r 2         # 2 lines/sec
python ratelimit.py exec "curl http://api" -r 5 -n 100  # 5/sec, 100 total
python ratelimit.py wait "api-call" -r 0.5             # Distributed rate limit
```
## Zero dependencies. Python 3.6+.
