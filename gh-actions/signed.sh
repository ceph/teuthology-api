#!/bin/bash
set -ex
commmitmsg=$(git log -1 --no-merges $commit --pretty='%B')
printf "\n Commit: %s" "$commmitmsg"
trailer=$(git log -1 --no-merges $commit --pretty='%B' | git interpret-trailers --parse 2>&1)
printf "trailer: %s" "$trailer"
if [[ $trailer != Signed-off-by:* ]]; then
    printf '%s\n' "Commit is not signed, use git commit --amend --signoff" >&2
    exit 1
fi