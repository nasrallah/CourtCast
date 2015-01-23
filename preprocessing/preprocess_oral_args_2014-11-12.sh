#!/bin/bash
#echo ''
#echo 'copying and renaming files to new directory...'
#cd /Users/nasrallah/Desktop/test
#for f in *.txt
#do 
#    cp -v $f /Users/nasrallah/Desktop/test2/$f
#    #cp -v $f /Users/nasrallah/Desktop/test2/${f%.txt}$'_mod'.txt
#done

cd /Users/nasrallah/Desktop/test
for f in *.txt
do
    echo $f
    LC_CTYPE=C tr -cd '\11\12\15\40-\176' < $f > ${f%.txt}$'_1'.txt
    sed 's/[0-9]*//' ${f%.txt}$'_1'.txt > ${f%.txt}$'_2'.txt
    egrep -v 'Official|Alderson Reporting|\-\-\-\-\-\-' ${f%.txt}$'_2'.txt > ${f%.txt}$'_3'.txt
    grep '[[:graph:]]' ${f%.txt}$'_3'.txt > ${f%.txt}$'_mod'.txt
done

rm *_?.txt
