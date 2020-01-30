#!/bin/bash
cd $1
pwd
# 1 - remove ._ files
echo "Removing ._* files"
find . -type d -name ._\* -exec rm -rf {} \;
find . -type f -name ._\* -exec rm {} \;

# 2 - convert space to _ in names:
# Had problem with space-full directory under other space-full directory. Might need to check depth 1 first.
echo "Converting spaces in paths to _"
echo "* If there are issues, manually rename directories in the root to remove the space."
find -name "* *" -type d | rename 's/ /_/g'
find -name "* *" -type f | rename 's/ /_/g'

# 3 Flatten
echo "Flattening all files into root directory."
shopt -s globstar	# makes '**' match any levels of directory
rename -v 's:/:-:g' **/*.xml	# -n for dryrun, -v for verbose
rename -v 's:/:-:g' **/*.pdf

