import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class cpr extends Format
{
	name       = "Trzmiel";
	website    = "http://fileformats.archiveteam.org/wiki/Trzmiel";
	ext        = [".cpr"];
	idCheck    = async inputFile => (await fileUtil.readFileBytes(inputFile.absolute, 1))[0]===2;	// have not encountered any that start with anything other than 2
	converters = ["recoil2png[format:CPR]"];
}
