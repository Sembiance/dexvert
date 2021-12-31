import {Format} from "../../Format.js";

export class ttcomp extends Format
{
	name    = "TTComp Archive";
	website = "http://fileformats.archiveteam.org/wiki/TTComp_archive";
	magic   = ["TTComp archive"];
	
	// music/thomasHermann is mis-identified as ttcomp
	forbiddenExt = [".thm"];
	idCheck      = inputFile => inputFile.preExt!==".thm";

	// NOTE: Deark also supports extraction of these, but because deark will also convert so many other formats and TTComp is a very weak magic identification, we don't include it here
	converters = ["ttdecomp"];
}
