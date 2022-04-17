# Magazine Renamer

## What?
A small tool to rename IEEE magazines and more.

## Why?
As I plan to slim down what I store, and organize the remaining files, I wanted to organize the IEEE magazines I received over the years. As a part of this effort, I wanted rename them in bulk. Since some of the effort needed some computation and I failed to find a ready made tool, I've written my own.

## How?
The script gets a list of files, and runs a series of regular expression matches on them. Since the files are named with a pattern, it can detect the magazine and naming convention. Then it creates the new name and renames the file.

The tool should ignore the files it doesn't know, and shouldn't re-match already renamed files, so it's relatively safe to run it on a very crowded folder, but don't take my word on it, and be cautious. This is why there's a `--simulate` option implemented. Use it. The responsibility is yours. There's no warranty attached.

## Notes
The tool is coded quickly, so it's neither innovative, nor clever, nor optimized. I may clean the code and polish things as I use it and new features though.