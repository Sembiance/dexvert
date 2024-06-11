import {Format} from "../../Format.js";

export class pfsWrite extends Format
{
	name       = "Professional Write Document";
	website    = "http://fileformats.archiveteam.org/wiki/Pfs:Write";
	ext        = [".pfs"];
	magic      = ["Professional Write document", /^fmt\/1414( |$)/];
	converters = ["wordForWord", "fileMerlin[type:PFS*]"];
}
