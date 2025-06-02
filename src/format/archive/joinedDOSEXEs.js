import {Format} from "../../Format.js";

export class joinedDOSEXEs extends Format
{
	name           = "Concatenated DOS EXEs";
	website        = "http://fileformats.archiveteam.org/wiki/V-Load";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["16bit DOS V-Load joined executables"];
	converters     = ["splitDOSEXEs"];
}
