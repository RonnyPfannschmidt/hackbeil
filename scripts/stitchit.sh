#!/bin/bash

SOURCE=$1

USER=$(hg log -R $SOURCE -r 0 --template {author})

echo -n processing $SOURCE \ 
echo it has $(hg id -n -r tip -R $SOURCE) changes

echo removing .
hg st -An|xargs rm
echo archiving from $SOURCE
hg archive -R $SOURCE -r 0 .
rm .hg_archival.txt
hg addremove
hg diff
echo commiting first of $SOURCE

hg log -R $SOURCE -r 0 \
    --template 'AUTO: {desc}\n\nResult of the automated HG Convert\n' \
    |hg ci -l - --user $USER

echo importing patches from $SOURCE
hg export -R $SOURCE -r 1:: | hg import -
