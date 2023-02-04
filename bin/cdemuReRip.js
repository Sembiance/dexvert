import {xu} from "xu";
import {cmdUtil, runUtil} from "xutil";
import {path, delay} from "std";
import {XLog} from "xlog";

const xlog = new XLog();

// WARNING! This script assumes only 1 copy of it will be run at a time per system. Since right now this is only really done with top level ISO's this is a fair assumption
// However if an item had multiple ISOs that all need this script ran on them, this script would need to be modified to support multiple a central cdemu-daemon being started by dexserver and it would need to coordinate slot number availablity

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Will mount <inputFilePath> as an ISO to a virtual drive using CDEMU and then use cdrdao to re-rip it as a bin/cue saving into <outputDirPath>",
	args :
	[
		{argid : "inputFilePath", desc : "ISO file", required : true},
		{argid : "outputDirPath", desc : "Output directory to place generated BIN/CUE", required : true}
	]});

let xvfbPort=null, cb=null;

try
{
	await runUtil.run("sudo", ["modprobe", "vhba"]);
	({xvfbPort, cb} = await runUtil.run("sudo", ["cdemu-daemon"], {detached : true, virtualX : true}));

	await delay(xu.SECOND*5);

	let {stdout : cdemuStatus} = await runUtil.run("sudo", ["cdemu", "status"], {timeout : xu.SECOND*5, killChildren : true, env : {DISPLAY : `:${xvfbPort}`}});
	if(!cdemuStatus?.includes("0     False"))
	{
		await runUtil.run("sudo", ["killall", "cdemu-daemon"]);
		Deno.exit(xlog.warn`Failed to load cdemu-daemon`);
	}

	await runUtil.run("sudo", ["cdemu", "load", "0", path.resolve(argv.inputFilePath)], {env : {DISPLAY : `:${xvfbPort}`}});

	({stdout : cdemuStatus} = await runUtil.run("sudo", ["cdemu", "status"], {timeout : xu.SECOND*5, killChildren : true, env : {DISPLAY : `:${xvfbPort}`}}));
	if(!cdemuStatus?.includes("0     True"))
	{
		await runUtil.run("sudo", ["killall", "cdemu-daemon"]);
		Deno.exit(xlog.warn`Failed to load ISO with cdemu`);
	}

	await runUtil.run("cdrdao", ["read-cd", "--read-raw", "--datafile", "out.bin", "--device", "/dev/sr0", "out.toc"], {cwd : argv.outputDirPath});
	await runUtil.run("toc2cue", ["out.toc", "out.cue"], {cwd : argv.outputDirPath});
}
catch(err)
{
	console.error(err);
}

await runUtil.run("sudo", ["killall", "cdemu-daemon"]);	// can't kill the process with runUtil.kill(p) due to the way sudo works? Not even killChildren helped.
if(cb)
	await cb();
