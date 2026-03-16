#!/usr/bin/env python3
"""ratelimit - Rate-limit command execution or stdin lines."""
import argparse, sys, time, subprocess

def main():
    p = argparse.ArgumentParser(description='Rate limiter')
    sub = p.add_subparsers(dest='cmd')
    
    ln = sub.add_parser('lines', help='Rate-limit stdin lines')
    ln.add_argument('-r', '--rate', type=float, default=1, help='Lines per second')
    ln.add_argument('-b', '--burst', type=int, default=1, help='Burst allowance')
    
    ex = sub.add_parser('exec', help='Rate-limit command execution')
    ex.add_argument('command', nargs='+')
    ex.add_argument('-r', '--rate', type=float, default=1, help='Executions per second')
    ex.add_argument('-n', '--count', type=int, help='Total executions')
    
    wt = sub.add_parser('wait', help='Wait until rate allows')
    wt.add_argument('key', help='Rate limit key')
    wt.add_argument('-r', '--rate', type=float, default=1)
    wt.add_argument('--state-file', default='/tmp/ratelimit_state.json')
    
    args = p.parse_args()
    if not args.cmd: p.print_help(); return
    
    if args.cmd == 'lines':
        interval = 1.0 / args.rate
        tokens = args.burst
        last = time.time()
        for line in sys.stdin:
            now = time.time()
            tokens = min(args.burst, tokens + (now - last) * args.rate)
            last = now
            if tokens < 1:
                wait = (1 - tokens) / args.rate
                time.sleep(wait)
                tokens = 0
            else:
                tokens -= 1
            sys.stdout.write(line)
            sys.stdout.flush()
    
    elif args.cmd == 'exec':
        interval = 1.0 / args.rate
        cmd = ' '.join(args.command)
        i = 0
        while args.count is None or i < args.count:
            start = time.time()
            r = subprocess.run(cmd, shell=True)
            i += 1
            elapsed = time.time() - start
            if elapsed < interval:
                time.sleep(interval - elapsed)
    
    elif args.cmd == 'wait':
        import json, os, fcntl
        sf = args.state_file
        interval = 1.0 / args.rate
        
        state = {}
        if os.path.exists(sf):
            try:
                with open(sf) as f: state = json.load(f)
            except: pass
        
        last = state.get(args.key, 0)
        now = time.time()
        wait = max(0, interval - (now - last))
        if wait > 0:
            time.sleep(wait)
        
        state[args.key] = time.time()
        with open(sf, 'w') as f: json.dump(state, f)

if __name__ == '__main__':
    main()
