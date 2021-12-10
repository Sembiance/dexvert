import {Format} from "../../Format.js";

export class ttcomp extends Format
{
	name    = "TTComp Archive";
	website = "http://fileformats.archiveteam.org/wiki/TTComp_archive";
	magic   = ["TTComp archive"];
	
	// music/thomasHermann is mis-identified as ttcomp
	forbiddenExt = [".thm"];
	idCheck      = inputFile => inputFile.preExt!==".thm";

	converters = ["ttdecomp"];
}
