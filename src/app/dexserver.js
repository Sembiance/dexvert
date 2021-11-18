import {xu, fg} from "xu";
import {fileUtil} from "xutil";
import {Server} from "../Server.js";
import {path} from "std";

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

async function handleQuit()
{
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

async function getKeyPress()
{
	const buffer = new Uint8Array(1024);
	Deno.setRaw(Deno.stdin, true);
	await Deno.stdin.read(buffer);
	Deno.setRaw(Deno.stdin, false);
	return String.fromCharCode(buffer.at(0));
}
async function waitForQuit()
{
	const buffer = [];
	while(true)
	{
		const key = await getKeyPress();
		xu.stdoutWrite(fg.red(xu.c.blink + key));
		buffer.push(key);
		while(buffer.length>4)
			buffer.shift();
		if(buffer.join("")==="quit")
		{
			await handleQuit();
			break;
		}
	}
}
waitForQuit();	// eslint-disable-line unicorn/prefer-top-level-await

xu.log`Waiting for ${Object.keys(servers).length} servers to fully load...`;
for(const [serverid, server] of Object.entries(servers))
{
	xu.log`Waiting on server ${fg.peach(serverid)}...`;
	await xu.waitUntil(async () => (await server.status())===true);
	xu.log`Server ${fg.peach(serverid)} fully loaded!`;
}

xu.log`\nServers fully loaded! Took: ${((performance.now()-startedAt)/xu.SECOND).secondsAsHumanReadable()}`;

await fileUtil.writeFile(path.join(DEXVERT_RAM_DIR, "serverRunning"), "true");

xu.log`Type ${fg.peach("quit")} to quit`;
