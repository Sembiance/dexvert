import {xu} from "xu";
import {cmdUtil} from "xutil";
import {formats, init as initFormats} from "../src/format/formats.js";
import {WEAK_VALUES, IGNORE_MAGICS} from "../src/WEAK.js";
import {XLog} from "xlog";
import {flexMatch} from "../src/identify.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "findMatchingMagics",
	version : "1.0.0",
	desc    : "Finds and shows any magics that match the given magic",
	opts    :
	{
		logLevel   : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"}
	},
	args :
	[
		{argid : "magic", desc : "Which magic to check", required : true}
	]});
const xlog = new XLog(argv.logLevel);

xlog.info`Loading formats...`;
await initFormats(xlog);

for(const m of WEAK_VALUES)
{
	if(flexMatch(argv.magic, m))
		xlog.info`WEAK_VALUES: ${m}`;
}

for(const m of IGNORE_MAGICS)
{
	if(flexMatch(argv.magic, m))
		xlog.info`IGNORE_MAGICS: ${m}`;
}

for(const format of Object.values(formats))
{
	for(const m of Array.force(format.magic || []))
	{
		if(flexMatch(argv.magic, m))
			xlog.info`FORMAT ${format.formatid}: ${m}`;
	}
}
