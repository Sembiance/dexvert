import {Format} from "../../Format.js";

export class firstChoice extends Format
{
	name       = "First Choice Document";
	ext        = [".doc", ".pfs"];
	weakExt    = true;
	magic      = ["First Choice document"];
	converters = ["fileMerlin[type:PFSFC*]"];
}
