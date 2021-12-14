import {Format} from "../../Format.js";

export class pfsWrite extends Format
{
	name       = "Professional Write Document";
	magic      = ["Professional Write document"];
	converters = ["fileMerlin[type:PFS*]"];
}
