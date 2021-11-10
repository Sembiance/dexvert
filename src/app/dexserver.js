import {xu} from "xu";
import {fileUtil, runUtil} from "xutil";
import { delay } from "https://deno.land/std@0.113.0/async/mod.ts";

const DEXVERT_RAM_DIR = "/mnt/ram/dexvert";

const startedAt = performance.now();

xu.log`Cleaning up previous dexvert RAM installation...`;
if(await fileUtil.exists(DEXVERT_RAM_DIR))
	await Deno.remove(DEXVERT_RAM_DIR, {recursive : true});
await Deno.mkdir(DEXVERT_RAM_DIR, {recursive : true});

const pids = [];

xu.log`Starting servers...`;
if(!Deno.env.get("DISPLAY"))
{
	xu.log`No X display detected. Starting X...`;
	pids.push(await runUtil.run("X", [], {detached : true}));
	await xu.waitUntil(fileUtil.exists("/tmp/.X0-lock"));
	await delay(xu.SECOND*2);
	xu.log`Starting dbus-launch...`;
	await runUtil.run("dbus-launch", ["--exit-with-x11"], {env : {DISPLAY : ":0", detached : true}});
}

["SIGINT", "SIGTERM"].map(v => Deno.addSignalListener(v, () => signalHandler(v)));
function signalHandler(sig)
{
	xu.log`Got signal ${sig}`;
	//xu.log`Closing ${pids.length} children...`;
	//for(const pid of pids)
	//	pid.kill("SIGTERM");
	xu.log`Exiting...`;
	Deno.exit(0);
}

xu.log`Servers running! Took: ${((performance.now()-startedAt)/xu.SECOND).secondsAsHumanReadable()}`;

await delay(xu.YEAR);


/*
../server/server.js &
KIDPIDS+=($!)

../tensor/runTensorServer.sh &
KIDPIDS+=($!)

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
