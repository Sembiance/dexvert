import {xu, fg} from "xu";
import {fileUtil} from "xutil";
import {Server} from "../Server.js";
import {path, delay} from "std";

const DEXVERT_RAM_DIR = "/mnt/ram/dexvert";

const startedAt = performance.now();

xu.log`Cleaning up previous dexvert RAM installation...`;
await fileUtil.unlink(DEXVERT_RAM_DIR, {recursive : true});
await Deno.mkdir(DEXVERT_RAM_DIR, {recursive : true});

const servers = await Server.loadServers();

xu.log`Starting ${Object.keys(servers).length} servers...`;
for(const [serverid, server] of Object.entries(servers))
{
	xu.log`Starting server ${fg.peach(serverid)}...`;
	await server.start();
	xu.log`Server ${fg.peach(serverid)} started!`;
}

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

xu.log`Waiting for ${Object.keys(servers).length} servers to fully load...`;
for(const [serverid, server] of Object.entries(servers))
{
	xu.log`Waiting on server ${fg.peach(serverid)}...`;
	await xu.waitUntil(async () => (await server.status())===true);
	xu.log`Server ${fg.peach(serverid)} fully loaded!`;
}

xu.log`\nServers fully loaded! Took: ${((performance.now()-startedAt)/xu.SECOND).secondsAsHumanReadable()}`;

await fileUtil.writeFile(path.join(DEXVERT_RAM_DIR, "serverRunning"), "true");

await delay(xu.YEAR);
