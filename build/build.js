import {xu} from "xu";
import {printUtil, cmdUtil} from "xutil";

import {default as formats} from "./targets/formats.js";
import {default as programs} from "./targets/programs.js";
import {default as README} from "./targets/README.js";
import {default as SUPPORTED} from "./targets/SUPPORTED.js";
import {default as UNSUPPORTED} from "./targets/UNSUPPORTED.js";
const TARGETS = Object.fromEntries([["formats", formats], ["programs", programs], ["README", README], ["SUPPORTED", SUPPORTED], ["UNSUPPORTED", UNSUPPORTED]]);

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Builds one or more targets",
	opts    :
	{
		silent : {desc : "Don't output any messages"}
	},
	args :
	[
		{argid : "target", desc : "The target to build", required : true, multiple : true, allowed : ["all", ...Object.keys(TARGETS)]}
	]});

if(!argv.silent)
	xu.verbose = 3;

const targets = (argv.target.some(v => v.toLowerCase()==="all") ? Object.keys(TARGETS) : argv.target);
for(const [i, target] of Object.entries(targets))
{
	xu.log3`${printUtil.majorHeader(target, +i>0 ? {prefix : "\n"} : {})}`;
	await TARGETS[target]();
}
