import {xu, fg} from "xu";
import {fileUtil} from "xutil";
import {delay} from "https://deno.land/std@0.113.0/async/mod.ts";
import {Server} from "../Server.js";

const DEXVERT_RAM_DIR = "/mnt/ram/dexvert";

const startedAt = performance.now();

xu.log`Cleaning up previous dexvert RAM installation...`;
if(await fileUtil.exists(DEXVERT_RAM_DIR))
	await Deno.remove(DEXVERT_RAM_DIR, {recursive : true});
await Deno.mkdir(DEXVERT_RAM_DIR, {recursive : true});

const servers = await Server.loadServers();

xu.log`Starting ${Object.keys(servers).length} servers...`;
for(const [serverid, server] of Object.entries(servers))
{
	xu.log`Starting server ${fg.peach(serverid)}...`;
	await server.start();
	xu.log`Server ${fg.peach(serverid)} started!`;
}

xu.log`Waiting for ${Object.keys(servers).length} servers to fully load...`;
for(const [serverid, server] of Object.entries(servers))
{
	await xu.waitUntil(async () => (await server.status())===true, xu.SECOND);
	xu.log`Server ${fg.peach(serverid)} fully loaded!`;
}

xu.log`\nServers fully loaded! Took: ${((performance.now()-startedAt)/xu.SECOND).secondsAsHumanReadable()}`;

["SIGINT", "SIGTERM"].map(v => Deno.addSignalListener(v, async () => await signalHandler(v)));
async function signalHandler(sig)
{
	xu.log`Got signal ${sig}`;

	xu.log`Stopping ${Object.keys(servers).length} servers...`;
	for(const [serverid, server] of Object.entries(servers))
	{
		xu.log`Stopping server ${fg.peach(serverid)}...`;
		await server.stop();
		xu.log`Server ${fg.peach(serverid)} stopped.`;
	}
	
	xu.log`Exiting...`;
	Deno.exit(0);
}

await delay(xu.YEAR);
