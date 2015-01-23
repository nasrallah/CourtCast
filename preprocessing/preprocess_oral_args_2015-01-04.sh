#!/bin/bash
#### This script preprocesses the txt files resulting from the pdf to txt conversion to clean them up.
#### It does the following things:
#### 1. removes non-ASCII characters [LC_CTYPE]
#### 2. removes numbers or whitespace at the beginning of lines (line numbers) [sed]
#### 3. removes the "Alderson Reporting Company -------... from each page [egrep]
#### 4. removes all whitespace lines [grep]
#### 5. saves the file as filename_mod.txt

#### 2015-01-04 edit. Modified Step 2 (sed command) to remove only numbers beginning lines followed by whitespace or whitespace alone.

for f in *.txt
do
    #echo $f
    LC_CTYPE=C tr -cd '\11\12\15\40-\176' < $f | 
    sed 's/^[0-9]*[[:space:]]//' |
    egrep -v 'Official|Alderson Reporting|\-\-\-\-\-\-' | 
    grep '[[:graph:]]' > ${f%.txt}$'_mod'.txt
done


#### Older bit if you wanted to copy files to a new directory first.
#!/bin/bash
#echo ''
#echo 'copying and renaming files to new directory...'
#cd /Users/nasrallah/Desktop/test
#for f in *.txt
#do 
#    cp -v $f /Users/nasrallah/Desktop/test2/$f
#    #cp -v $f /Users/nasrallah/Desktop/test2/${f%.txt}$'_mod'.txt
#done