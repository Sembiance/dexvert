import {Format} from "../../Format.js";

export class pfsWrite extends Format
{
	name       = "Professional Write Document";
	magic      = ["Professional Write document", /^fmt\/1414( |$)/];
	converters = ["fileMerlin[type:PFS*]"];
}
