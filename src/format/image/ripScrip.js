import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class ripScrip extends Format
{
	name       = "Remote Imaging Protocol Script";
	website    = "http://fileformats.archiveteam.org/wiki/RIPscrip";
	ext        = [".rip"];
	magic      = ["RIPscript", "ANSI escape sequence text"];
	weakMagic  = ["ANSI escape sequence text"];
	idCheck    = async inputFile => (await fileUtil.readFileBytes(inputFile.absolute, Math.min(32, inputFile.size))).indexOfX([0x21, 0x7C])!==-1;
	converters = ["pabloDraw"];
}
