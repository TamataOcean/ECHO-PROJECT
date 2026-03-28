#!/usr/bin/env python3
"""
Met à jour les variables NAS_* dans /app/config.env.
Usage : update_nas_config.py KEY=VALUE KEY2=VALUE2 ...
Note : les valeurs ne doivent pas contenir d'espaces.
"""
import sys, re

F = '/app/config.env'

try:
    c = open(F).read()
except FileNotFoundError:
    c = ''

for arg in sys.argv[1:]:
    if '=' not in arg:
        continue
    key, val = arg.split('=', 1)
    pattern = r'^' + re.escape(key) + r'=.*'
    replacement = key + '=' + val
    if re.search(pattern, c, flags=re.M):
        c = re.sub(pattern, replacement, c, flags=re.M)
    else:
        c = c.rstrip('\n') + '\n' + replacement + '\n'

open(F, 'w').write(c)
print('ok')
