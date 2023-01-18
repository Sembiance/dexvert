#!/bin/bash
#
# @copyright (c) 2011 Mark Moran, Western New England College
# @license MIT, See LICENSE  
#
# To call this script on all files recursively try. 
# Note: Calling more than once on a directory creates backups of encryped backups.
# 
# find . -type f -exec ~/cfdecrypt/cfdecrypt.sh "{}" \;

cfdecrypt_home=/mnt/compendium/DevLab/dexvert/bin/cfdecrypt/;
verbose=0;

function iscrypted 
{
	if [ ! -f $input_file ]; then echo "File Not Found"; exit 1; fi  #Make sure the file exists 
	if $cfdecrypt_home/cfiscrypted < $input_file; then echo "IS encrypted"; exit 0; else echo "NOT encrypted"; exit 1; fi;
}

function decrypt
{
	if [ "$verbose" = 1 ]; then echo "	Processing $input_file.."; fi 
	if [ ! -f "$input_file" ]; then echo "File Not Found"; exit 1; fi  #Make sure the file exists 
	if [ "$output_file" = "" ]; then output_file=$input_file; fi
	if [ "$backup_file" = "" ]; then backup_file=$input_file"_crypted"; fi
	
	if $cfdecrypt_home/cfiscrypted < "$input_file"; then
		
		if ! cp "$input_file" "$backup_file"; then 
			echo "Error writing backup file: "$backup_file; 
			exit 1; 
		fi
		
		if ! touch "$input_file""_temp_decrypted"; then 
			echo "Error writing temp file: "$input_file"_temp_decrypted"; 
			exit 1; 
		fi
		
		if $cfdecrypt_home/cfdecrypt < "$input_file" > "$input_file""_temp_decrypted"; then 
			if [ "$verbose" = 1 ]; then 
				echo "Decrypted $input_file to $output_file, backup: $backup_file"; 
			else
				echo "Decrypted $input_file";
			fi
		fi
		
		if ! mv "$input_file""_temp_decrypted" $output_file; then 
			echo "Error. Unable to write $output_file"; 
			exit 1; 
		fi
		exit 0;
	elif [ "$verbose" = 1 ]; then 
			echo "File Not Encrypted: $input_file";
	fi	
}

function usage
{
    echo ;
	echo "Usage: ";
	echo "  cfdecrypt.sh [options] [-f] input_file";
	echo ;
	echo "  options:";
	echo "    -c,  --iscrypted  only check if the specified file is encrypted";
	echo "    -o,  --output     specify an output file, default: backup and overwrite the original";
	echo "    -b,  --backup     specify the backup filename, default is to append '_backup' to the original filename";
	echo ;
	echo "    -v,  --verbose    More verbose output";
	echo "    -h,  --help       displays this help screen";
	
	exit;
}


if [ "$1" = "" ]; then usage; exit; fi;
while [ "$1" != "" ]; do
    case $1 in
	-f | --file | --input)	shift
				input_file=$1
				;;
							
	-o | --output )		shift
				output_file=$1
				;;
	-b | --backup )		shift
				backup_file=$1
				;;

	-c | --iscrypted )	shift
				if [ "$input_file" = "" ]; then input_file=$1; fi;
				iscrypted
				exit
				;;
							
	-v | --verbose )        verbose=1;
				;;		
							
	-h | --help )		usage
				exit
				;;

	-* )			echo ; echo "ERROR. Unknown option  $1"; 
				usage
				exit
				;;
	* )                     input_file=$1
			
    esac
    shift
done

decrypt #if script hasn't exited yet, run the default decrypt function
