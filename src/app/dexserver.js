import {xu, fg} from "xu";
import {fileUtil, runUtil} from "xutil";
import {path, delay} from "std";

const xlog = xu.xLog();

const DEXVERT_RAM_DIR = "/mnt/ram/dexvert";
const DEXSERVER_PID_FILE_PATH = path.join(DEXVERT_RAM_DIR, "dexserver.pid");
const SERVER_ORDER = ["xdisplay", "ftp", "tensor", "qemu"];

const startedAt = performance.now();
const servers = Object.fromEntries(await SERVER_ORDER.parallelMap(async serverid => [serverid, (await import(path.join(xu.dirname(import.meta), `../server/${serverid}.js`)))[serverid].create(xlog)]));

if(await fileUtil.exists(DEXSERVER_PID_FILE_PATH))
{
	xlog.info`Killing previous dexserver instance...`;
	const prevDexservPID = await Deno.readTextFile(DEXSERVER_PID_FILE_PATH);
	await runUtil.run("kill", [prevDexservPID]);
	await fileUtil.unlink(DEXSERVER_PID_FILE_PATH);
}

xlog.info`Cleaning up previous dexvert RAM installation...`;
await fileUtil.unlink(DEXVERT_RAM_DIR, {recursive : true});
await Deno.mkdir(DEXVERT_RAM_DIR, {recursive : true});

async function signalHandler(sig)
{
	xlog.info`Got signal ${sig}`;

	xlog.info`Stopping ${Object.keys(servers).length} servers...`;
	for(const serverid of SERVER_ORDER.reverse())
	{
		xlog.info`Stopping server ${fg.peach(serverid)}...`;
		try
		{
			await servers[serverid].stop();
		}
		catch {}
		xlog.info`Server ${fg.peach(serverid)} stopped.`;
	}
	
	await fileUtil.unlink(DEXSERVER_PID_FILE_PATH);
	xlog.info`Exiting...`;
	Deno.exit(0);
}
["SIGINT", "SIGTERM"].map(v => Deno.addSignalListener(v, async () => await signalHandler(v)));

xlog.info`Starting ${Object.keys(servers).length} servers...`;
for(const serverid of SERVER_ORDER)
{
	const server = servers[serverid];
	xlog.info`Starting server ${fg.peach(serverid)}...`;
	await server.start();
	xlog.info`Server ${fg.peach(serverid)} started, waiting for fully loaded...`;
	await xu.waitUntil(async () => (await server.status())===true);
	xlog.info`Server ${fg.peach(serverid)} fully loaded!`;
}

await Deno.writeTextFile(DEXSERVER_PID_FILE_PATH, `${Deno.pid}`);
xlog.info`\nServers fully loaded! Took: ${((performance.now()-startedAt)/xu.SECOND).secondsAsHumanReadable()}`;

await delay(xu.YEAR);	// gonna run into an issue if it runs longer than 1 year rofl
