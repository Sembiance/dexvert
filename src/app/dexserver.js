import {xu} from "xu";
import {fileUtil, runUtil} from "xutil";
import { delay } from "https://deno.land/std@0.113.0/async/mod.ts";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import * as fs from "https://deno.land/std@0.111.0/fs/mod.ts";

const DEXVERT_RAM_DIR = "/mnt/ram/dexvert";

const startedAt = performance.now();

xu.log`Cleaning up previous dexvert RAM installation...`;
if(await fileUtil.exists(DEXVERT_RAM_DIR))
	await Deno.remove(DEXVERT_RAM_DIR, {recursive : true});
await Deno.mkdir(DEXVERT_RAM_DIR, {recursive : true});

const procs = [];

xu.log`Starting servers...`;

// If we don't have a DISPLAY variable, start up a background X display
if(!Deno.env.get("DISPLAY"))
{
	xu.log`No X display detected. Starting X...`;
	procs.push(await runUtil.run("X", [], {detached : true, liveOutput : true}));
	await xu.waitUntil(fileUtil.exists("/tmp/.X0-lock"));
	await delay(xu.SECOND*2);
	xu.log`Starting dbus-launch...`;
	await runUtil.run("dbus-launch", ["--exit-with-x11"], {env : {DISPLAY : ":0", detached : true, liveOutput : true}});
}

// Start up our tensor server
const TENSOR_SRC_DIR = path.join(xu.dirname(import.meta), "../../tensor");
const TENSOR_WIP_DIR = "/mnt/ram/dexvert/tensor";

xu.log`Removing existing tensor wip directories...`;
await Deno.remove(TENSOR_WIP_DIR, {recursive : true}).catch(() => {});

xu.log`Creating tensor wip directories...`;
for(const name of ["__pycache__", "garbage", "tmp"])
	await Deno.mkdir(path.join(TENSOR_WIP_DIR, name), {recursive : true});

xu.log`Copying tensor files...`;
for(const name of ["tensorServer.sh", "tensorServer.py", "TensorModel.py", "garbage/model"])
	await fs.copy(path.join(TENSOR_SRC_DIR, Array.isArray(name) ? name[0] : name), path.join(TENSOR_WIP_DIR, Array.isArray(name) ? name[1] : name));

xu.log`Running tensor server docker...`;
const dockerArgs = ["run", "--name", "dexvert-tensor", "--gpus", "all", "--rm", "-p", "127.0.0.1:17736:17736", "-v", `${TENSOR_WIP_DIR}:${TENSOR_WIP_DIR}`, "-w", TENSOR_WIP_DIR, "tensorflow/tensorflow:latest-gpu", "./tensorServer.sh"];
await runUtil.run("docker", dockerArgs, {detached : true, liveOutput : true, cwd : TENSOR_WIP_DIR});

// Now wait for our servers to fully load
xu.log`Waiting for servers to fully load...`;
await xu.waitUntil(async () => (await (await fetch("http://localhost:17736/status").catch(() => {}))?.json())?.status==="a-ok", xu.SECOND);
xu.log`Tensor server started!`;

["SIGINT", "SIGTERM"].map(v => Deno.addSignalListener(v, async () => await signalHandler(v)));
async function signalHandler(sig)
{
	xu.log`Got signal ${sig}`;

	xu.log`Closing ${procs.length} children...`;
	for(const proc of procs)
		try { proc.kill("SIGTERM"); } catch{}	// eslint-disable-line brace-style

	xu.log`Stopping tensor...`;
	await runUtil.run("docker", ["stop", "dexvert-tensor"]);
	
	xu.log`Exiting...`;
	Deno.exit(0);
}

xu.log`Servers running! Took: ${((performance.now()-startedAt)/xu.SECOND).secondsAsHumanReadable()}`;

await delay(xu.YEAR);


/*
../server/server.js &
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
