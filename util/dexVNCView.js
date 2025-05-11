import {xu} from "xu";
import {cmdUtil, runUtil} from "xutil";
import {XLog} from "xlog";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Opens up a bunch of dexvert OS VNC windows for a target machine",
	args :
	[
		{argid : "osid", desc : "Which OS to open", required : true},
		{argid : "host", desc : "Which host to open from", required : true}
	]});

const xlog = new XLog();

if(["127.0.0.1", "localhost"].includes(argv.host))
	argv.host = Deno.hostname();

const {stdout} = await runUtil.run("ssh", [argv.host, `curl "http://127.0.0.1:17735/status"`]);
const osStatus = xu.parseJSON(stdout);
const vncPorts = Object.values(osStatus.instances[argv.osid]).map(o => o.vncPort);

const procs = [];
const cbs = [];
for(const vncPort of vncPorts)
{
	const {p, cb} = await runUtil.run("/mnt/compendium/bin/vncRemote", [`--vncPort=${vncPort}`, argv.host], {detached : true, inheritEnv : true});
	procs.push(p);
	cbs.push(cb);
}

async function signalHandler(sig)
{
	xlog.info`Got signal ${sig}`;
	for(const p of procs)
		await runUtil.kill(p);

	Deno.exit(0);
}
["SIGINT", "SIGTERM"].map(v => Deno.addSignalListener(v, async () => await signalHandler(v)));

await Promise.all(cbs);
