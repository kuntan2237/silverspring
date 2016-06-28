#!/usr/bin/env python3
# This wrapper is used to generate config.example from exting config file
# Of cause all private keys should be cleaned before commit

import re

print('Copy config to config.example without key strings...', end='')
with open('config', 'r') as r, open('config.example', 'w+') as w:
    for line in r:
        if 'key:' in line:
            line = line.split()[0] + ' ' \
                   + re.subn('[a-z, A-Z, 0-9]', 'x', line.split()[1])[0] + '\n'
        w.write(line)
print('Done.')
