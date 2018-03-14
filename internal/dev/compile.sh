#!/usr/bin/env bash
gcc -c -fPIC main.c -o main.o
gcc main.o -shared -o main.so
