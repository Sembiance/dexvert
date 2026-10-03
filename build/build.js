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
		silent   : {desc : "Don't output any messages"},
		logLevel : {desc : "Log level to use", defaultValue : "info"}
	},
	args :
	[
		{argid : "target", desc : "The target to build", required : true, multiple : true, allowed : ["all", ...TARGET_NAMES]}
	]});

const xlog = new XLog(argv.silent ? "none" : argv.logLevel);

// don't be tempted to parallelMap this, unless you do initRegistry yourself first (to avoid trouncing on each other), but at that point there isn't much time savings anymore
for(const targetid of (argv.target.some(v => v.toLowerCase()==="all") ? TARGET_NAMES.subtractOnce(ALL_EXEMPT) : argv.target))
{
	xlog.info`${targetid.padStart(TARGET_NAMES.map(v => v.length).max())} ::: Building...`;
	await (await import(path.join(import.meta.dirname, "targets", `${targetid}.js`))).default(xlog);
	xlog.info`${targetid.padStart(TARGET_NAMES.map(v => v.length).max())} ::: Complete!`;
}
