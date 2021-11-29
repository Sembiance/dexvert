import {Format} from "../../Format.js";

export class symDef extends Format
{
	name       = "SYMDEF File";
	ext        = [".symdef"];
	magic      = [/^data$/];
	weakMagic  = true;
	converters = ["strings"];
}
