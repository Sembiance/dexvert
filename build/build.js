import {xu} from "xu";
import {printUtil, cmdUtil} from "xutil";
import {path} from "std";

const TARGET_NAMES = ["programs", "formats", "README", "SUPPORTED", "UNSUPPORTED"];
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

if(!argv.silent)
	xu.verbose = 3;

const targetids = (argv.target.some(v => v.toLowerCase()==="all") ? TARGET_NAMES : argv.target);
for(const [i, targetid] of Object.entries(targetids))
{
	xu.log3`${printUtil.majorHeader(targetid, +i>0 ? {prefix : "\n"} : {})}`;

	// DO not be tempted to make the import static because the 'formats.js' outtput file might point to files that no longer exist and README/SUPPORTED/UNSUPPORTED targets load this
	await (await import(path.join(xu.dirname(import.meta), "targets", `${targetid}.js`))).default();
}
