#!/bin/bash
set -e
echo "print your nonsense > "
cat > code.c
gcc code.c -o a.out 2>&1
./a.out
rm -rf a.out
