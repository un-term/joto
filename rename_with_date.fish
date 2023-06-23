#!/usr/bin/env fish

set filepath $argv
echo $filepath
set filename (basename $filepath)
echo $filename
set fileext (string split -r -m1 . $filename)[2]
echo $fileext
set dirpath (dirname $filepath)
echo $dirpath

# check if patterns match first and then reformat if needed

# echo $filename | grep -o "....-..-.."
# if [ $status -eq 0 ]
#     set date_var (echo $filename | grep -o "....-..-..")
# end

echo $filename | grep -o "_........_"
if [ $status -eq 0 ]
    echo "Formatting date"
    set uf_date (echo $filename | grep -o "_........_")
    set year (string sub -s 2 -l 4 $uf_date)
    set month (string sub -s 6 -l 2 $uf_date)
    set day (string sub -s 8 -l 2 $uf_date)
    set f_date $year"-"$month"-"$day
end

echo $f_date

echo "Give description to file:"
set img_drpt (read -l) 

set new_filepath $dirpath/$f_date"_"$img_drpt"."$fileext
echo "Setting new file name: $new_filepath"
