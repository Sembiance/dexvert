#!/bin/bash

# So this script essentially transfers files into the QEMU dexserver image, runs dexvert commands to process the files and then transfers the resulting files back out

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

useJSON=0
keepGoing=0
tmpDir="/tmp"
logLevel="info"
suffix="§"

showUsage() {
    echo "Usage: $0 [--json] [--keepGoing] [--tmpDir <dir>] [--logLevel none fatal error warn info(default) debug trace] [--suffix suffix (default: §)] inputFile outputDir"
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

echo "Transferring files to QEMU instance..."
inputDir="$inputFile"

if [[ -f "$inputFile" ]]; then
	inputDir="$(dirname "$inputFile")"
fi

inTar="$tmpDir/$(generate_random_string).tar"
curPWD=$(pwd)

cd "$inputDir" || exit
tar -cf "$inTar" --no-recursion ./*

scp -q -i "$SCRIPT_DIR"/dexvert-ssh-key -P 47022 "$inTar" dexvert@127.0.0.1:/mnt/dexvert/in.tar
rm -f "$inTar"
runSSHCmd "tar --directory /mnt/dexvert/in -xf /mnt/dexvert/in.tar"
runSSHCmd "rm -f /mnt/dexvert/in.tar"

cd "$curPWD" || exit

performDexing() {
	runSSHCmd "mkdir /mnt/dexvert/out/\"$1\"$suffix"
	if [[ $keepGoing -eq 1 ]]; then
		runSSHCmd "/mnt/compendium/.deno/bin/dexrecurse --logLevel=${logLevel} $([ $useJSON -eq 1 ] && echo " --json") \"/mnt/dexvert/in/$1\" /mnt/dexvert/out"
	else
		runSSHCmd "/mnt/compendium/.deno/bin/dexvert --logLevel=${logLevel} $([ $useJSON -eq 1 ] && echo " --jsonFile=/mnt/dexvert/out/\"$1\"$suffix.json") \"/mnt/dexvert/in/$1\" /mnt/dexvert/out/\"$1\"$suffix"
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
