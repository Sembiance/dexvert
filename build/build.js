import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";
import {path} from "std";

const TARGET_NAMES = ["README", "SUPPORTED", "UNSUPPORTED", "programsFormats"];
const ALL_EXEMPT = ["programsFormats"];

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

const targetids = (argv.target.some(v => v.toLowerCase()==="all") ? TARGET_NAMES.subtractOnce(ALL_EXEMPT) : argv.target);
await targetids.parallelMap(async targetid =>
{
	xlog.info`${targetid.padStart(TARGET_NAMES.map(v => v.length).max())} ::: Building...`;
	await (await import(path.join(import.meta.dirname, "targets", `${targetid}.js`))).default(xlog);
	xlog.info`${targetid.padStart(TARGET_NAMES.map(v => v.length).max())} ::: Complete!`;
});
