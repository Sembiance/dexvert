import {Format} from "../../Format.js";

export class bsaveCompressed extends Format
{
	name           = "BSAVE Compressed";
	website        = "http://fileformats.archiveteam.org/wiki/PCPaint_BSAVE";
	ext            = [".pic", ".img"];
	forbidExtMatch = true;
	magic          = ["deark: bsave_cmpr"];
	converters     = ["deark[module:bsave_cmpr][renameOut] -> deark[module:bsave][renameOut]"];
	classify       = true;
}
