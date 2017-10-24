#!/user/bin/expect
# ship the pdf to the abbyy server
# $1 has folder of source pdf
# $2 has filename w/o the .pdf extention
# send_to_abbyy.exp is in ./
src_folder="$1"
src_file_no_ext="$2"
/usr/bin/expect send_to_abbyy.exp ${src_folder} ${src_file_no_ext}
