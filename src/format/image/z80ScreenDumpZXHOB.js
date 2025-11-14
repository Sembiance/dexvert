import {Format} from "../../Format.js";

export class z80ScreenDumpZXHOB extends Format
{
	name       = "Z80 Screen dump ZXHOB";
	ext        = [".$c"];
	magic      = ["Z80 Screen dump :zxhob:"];
	converters = ["nconvert[extractAll][format:zxhob]"];
}
