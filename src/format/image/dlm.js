import {Format} from "../../Format.js";

export class dlm extends Format
{
	name       = "Dir Logo Maker";
	website    = "http://fileformats.archiveteam.org/wiki/Dir_Logo_Maker";
	ext        = [".dlm"];
	fileSize   = 256;
	byteCheck  = [{offset : 0, match : ["B".charCodeAt(0)]}];	// eslint-disable-line unicorn/prefer-code-point
	converters = ["recoil2png"];
}
