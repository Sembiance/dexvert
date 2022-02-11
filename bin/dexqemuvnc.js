import {xu} from "xu";
import {cmdUtil, runUtil} from "xutil";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexqemuvnc",
	version : "1.0.0",
	desc    : "Opens one or more VNC windows to the dexvert QEMU servers",
	opts    :
	{
		dev : {desc : "Open up development windows instead of production"}
	},
	args :
	[
		{argid : "vncid", desc : "Which number or osid to open", required : true}
	]});

const OSID_SERVER_COUNT =
{
	win2k    : 16,
	winxp    : 16,
	amigappc : 8,
	gentoo   : 10
};

const OSID_OFFSET =
{
	win2k    : 100,
	winxp    : 200,
	amigappc : 300,
	gentoo   : 400
};

const OSIDs = ["win2k", "winxp", "amigappc", "gentoo"];
if(!argv.vncid.isNumber() && !OSIDs.includes(argv.vncid))
	Deno.exit(console.log(`Invalid VNCID. Must be a number or one of: ${OSIDs.join(" ")}`));

const vncNumbers = OSIDs.includes(argv.vncid) ? [].pushSequence(OSID_OFFSET[argv.vncid], OSID_OFFSET[argv.vncid]+(OSID_SERVER_COUNT[argv.vncid]-1)) : [+argv.vncid];

for(const vncNumber of vncNumbers)
{
	const localPort = argv.dev ? vncNumber : Math.randomInt(13000, 44000);
	if(!argv.dev)
		await runUtil.run("ssh", ["-f", "-o", "ExitOnForwardFailure=yes", "-L", `127.0.0.1:${localPort}:127.0.0.1:${vncNumber+5900}`, "chatsubo", "sleep", "5"], {inheritEnv : true, verbose : true, liveOutput : true});

	await runUtil.run("vncviewer", [`127.0.0.1:${localPort}`], {detached : true, inheritEnv : true});
}
