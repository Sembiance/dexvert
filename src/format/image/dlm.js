import {Format} from "../../Format.js";

export class dlm extends Format
{
	name       = "Dir Logo Maker";
	website    = "http://fileformats.archiveteam.org/wiki/Dir_Logo_Maker";
	ext        = [".dlm"];
	magic      = ["Dir Logo Maker bitmap"];
	fileSize   = 256;
	byteCheck  = [{offset : 0, match : ["B".charCodeAt(0)]}];
	converters = ["recoil2png"];
}
