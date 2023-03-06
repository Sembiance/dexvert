#!/bin/bash

# So this script essentially transfers files into the QEMU dexserver image, runs dexvert commands to process the files and then transfers the resulting files back out

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

useJSON=0
keepGoing=0
tmpDir="/tmp"
logLevel="info"
suffix="§"
osHint="dos"

showUsage() {
	echo "Usage: $0 [options] inputFile outputDir"
	echo "  --json               Produce some JSON for each file that is processed that details additional meta information about the file."
	echo "  --keepGoing          If this is set dexvert will keep converting any files it extracts, recursively."
	echo "  --tmpDir=<dir>       Set the tmp directory to use (default: /tmp)."
	echo "  --logLevel=<level>   How verbose to be. Valid: none fatal error warn info(default) debug trace"
	echo "  --suffix=<suffix>    Set the suffix to use for temporary files (default: §)."
	echo "  --osHint=<osid>      Provide a hint as to which Operating System this file was from. For options, see the readme.txt file"
	echo "  --help               Display this help message."
	exit 1
}

function generate_random_string() {
	tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w 10 | head -n 1
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --json)
            useJSON=1
            ;;
        --keepGoing)
            keepGoing=1
            ;;
        --suffix)
            if [[ -n "$2" ]]; then
                suffix="$2"
                shift
            else
                echo "Error: no value specified for --suffix"
                showUsage
            fi
            ;;
        --logLevel)
            if [[ -n "$2" ]]; then
                logLevel="$2"
                shift
            else
                echo "Error: no value specified for --logLevel"
                showUsage
            fi
            ;;
        --tmpDir)
            if [[ -n "$2" ]]; then
                tmpDir="$2"
                shift
            else
                echo "Error: no value specified for --tmpDir"
                showUsage
            fi
            ;;
        --osHint)
            if [[ -n "$2" ]]; then
                osHint="$2"
                shift
            else
                echo "Error: no value specified for --osHint"
                showUsage
            fi
            ;;
        -*)
            echo "Error: unrecognized option: $1"
            showUsage
            ;;
        *)
            if [[ -z "$inputFile" ]]; then
                inputFile="$1"
            elif [[ -z "$outputDir" ]]; then
                outputDir="$1"
            else
                echo "Error: too many arguments"
                showUsage
            fi
            ;;
    esac
    shift
done

if [[ -z "$inputFile" ]] || [[ -z "$outputDir" ]]; then
    showUsage
fi

if [[ ! -e "$inputFile" ]]; then
    echo "Error: $inputFile does not exist"
    showUsage
elif [[ ! -f "$inputFile" ]] && [[ ! -d "$inputFile" ]]; then
    echo "Error: $inputFile is not a regular file or directory"
    showUsage
fi

if [[ ! -d "$outputDir" ]]; then
    echo "Error: $outputDir is not a directory"
    showUsage
elif [[ "$(ls -A "$outputDir")" ]]; then
    echo "Error: $outputDir is not empty"
    showUsage
fi

runSSHCmd() {
	ssh -i "$SCRIPT_DIR"/dexvert-ssh-key -p 47022 dexvert@127.0.0.1 "$1"
}

echo "Preparing QEMU instance..."
runSSHCmd "rm -rf /mnt/dexvert/in /mnt/dexvert/out /mnt/dexvert/in.tar /mnt/dexvert/out.tar"
runSSHCmd "mkdir -p /mnt/dexvert/in /mnt/dexvert/out"

inputDir="$inputFile"

if [[ -f "$inputFile" ]]; then
	inputDir="$(dirname "$inputFile")"
fi

inTar="$tmpDir/$(generate_random_string).tar"
curPWD=$(pwd)

cd "$inputDir" || exit
totalSize=$(du -c -b --max-depth=1 | tail -n1 | cut -f1)
fileCount=$(find . -maxdepth 1 -type f | wc -l)
echo "Transferring $fileCount files totalling $((totalSize / 1024 / 1024)) MB to QEMU instance..."
tar -cf "$inTar" --no-recursion ./*

scp -q -i "$SCRIPT_DIR"/dexvert-ssh-key -P 47022 "$inTar" dexvert@127.0.0.1:/mnt/dexvert/in.tar
rm -f "$inTar"
runSSHCmd "tar --directory /mnt/dexvert/in -xf /mnt/dexvert/in.tar"
runSSHCmd "rm -f /mnt/dexvert/in.tar"

cd "$curPWD" || exit

performDexing() {
	runSSHCmd "mkdir /mnt/dexvert/out/\"$1\"$suffix"
	if [[ $keepGoing -eq 1 ]]; then
		runSSHCmd "/mnt/compendium/.deno/bin/dexrecurse --logLevel=${logLevel} --programFlag=oshint:${osHint}:true $([ $useJSON -eq 1 ] && echo " --json") \"/mnt/dexvert/in/$1\" /mnt/dexvert/out"
	else
		runSSHCmd "/mnt/compendium/.deno/bin/dexvert --logLevel=${logLevel} --programFlag=oshint:${osHint}:true $([ $useJSON -eq 1 ] && echo " --jsonFile=/mnt/dexvert/out/\"$1\"$suffix.json") \"/mnt/dexvert/in/$1\" /mnt/dexvert/out/\"$1\"$suffix"
	fi
}

if [[ -f "$inputFile" ]]; then
	performDexing "$(basename "$inputFile")"
elif [[ -d "$inputFile" ]]; then
	cd "$inputFile" || exit
	for file in ./*; do
		if [[ -f "$file" ]]; then
			performDexing "$file"
		fi
	done
fi

echo "Transferring files from QEMU instance..."
outTar="$tmpDir/$(generate_random_string).tar"
runSSHCmd "cd /mnt/dexvert/out && tar -cf /mnt/dexvert/out.tar ./*"
scp -q -i "$SCRIPT_DIR"/dexvert-ssh-key -P 47022 dexvert@127.0.0.1:/mnt/dexvert/out.tar "$outTar"
cd "$outputDir" || exit
tar -xf "$outTar"
rm -f "$outTar"
echo "Cleaning up..."
runSSHCmd "rm -rf /mnt/dexvert/in /mnt/dexvert/out /mnt/dexvert/in.tar /mnt/dexvert/out.tar"

echo "Done! Examine the results in: $outputDir"
