import {xu} from "xu";
import {cmdUtil, fileUtil, printUtil} from "xutil";
import {identify} from "../identify.js";
import {DexFile} from "../DexFile.js";

const DEXVERT_RAM_DIR = "/mnt/ram/dexvert";

xu.log`Cleaning up previous dexvert RAM installation...`;
if(await fileUtil.exists(DEXVERT_RAM_DIR))
	await Deno.remove(DEXVERT_RAM_DIR, {recursive : true});
await Deno.mkdir(DEXVERT_RAM_DIR, {recursive : true});

const pids = [];

xu.log`Starting servers...`;
if(!Deno.env.get("DISPLAY"))
{
	const pidX = await runUtil.run()
}
xu.log`${}`;
/*
#!/bin/bash

startAt=$(date +"%s")


echo "Starting servers..."

KIDPIDS=()

if [ "$DISPLAY" = "" ]
then
	echo "No X display detected. Starting X..."
	X &
	KIDPIDS+=($!)
	sleep 5
	DISPLAY=:0 dbus-launch --exit-with-x11
fi

../server/server.js &
KIDPIDS+=($!)

../tensor/runTensorServer.sh &
KIDPIDS+=($!)

function clean_up
{
	echo "Signal caught. Killing children..."
	for kidpid in "${KIDPIDS[@]}"; do
		kill "$kidpid"
	done

	echo "Waiting for children to finish..."
	wait

	echo -e "\033[0;32mdone.\033[0m"
	exit 1
}

trap clean_up SIGINT

# It will take some time for those servers to get going, so just sleep for a bit before outputting messages
sleep 40

for (( ; ; ))
do
	dexservStatusResult=$(curl --silent "http://localhost:17735/status" | jq ".status")
	tensorStatusResult=$(curl --silent "http://localhost:17736/status" | jq ".status")
	if [ "$dexservStatusResult" = '"a-ok"' ] && [ "$tensorStatusResult" = '"a-ok"' ]
	then
		break;
	else
		echo "Waiting for servers...   dex [${dexservStatusResult}]   tensor [${tensorStatusResult}]"
		sleep 5
	fi
done

endAt=$(date +"%s")
startupTimeDuration=$((endAt - startAt))

echo -e "\033[1;32mSERVERS ARE RUNNING!\033[0m (took $startupTimeDuration seconds)"

wait

*/
