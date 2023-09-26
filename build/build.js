import {xu} from "xu";
import {XLog} from "xlog";
import {printUtil, cmdUtil} from "xutil";
import {path} from "std";

const TARGET_NAMES = ["README", "SUPPORTED", "UNSUPPORTED", "release"];
const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Builds one or more targets",
	opts    :
	{
		silent : {desc : "Don't output any messages"}
	},
	args :
	[
		{argid : "target", desc : "The target to build", required : true, multiple : true, allowed : ["all", ...TARGET_NAMES]}
	]});

const xlog = new XLog(argv.silent ? "none" : "info");

const targetids = (argv.target.some(v => v.toLowerCase()==="all") ? TARGET_NAMES.subtractAll(["release"]) : argv.target);
for(const [i, targetid] of Object.entries(targetids))
{
	xlog.info`${printUtil.majorHeader(targetid, +i>0 ? {prefix : "\n"} : {})}`;
	await (await import(path.join(xu.dirname(import.meta), "targets", `${targetid}.js`))).default(xlog);
}
