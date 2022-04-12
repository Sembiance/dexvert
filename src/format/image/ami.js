import {Format} from "../../Format.js";

export class ami extends Format
{
	name       = "Amica Paint";
	website    = "http://fileformats.archiveteam.org/wiki/Amica_Paint";
	ext        = [".ami"];
	// recoil/view will almost convert anything, and there is no 'magic' so we just define a range of file sizes to limit junk that might get created
	idCheck    = inputFile => inputFile.size>1000 && inputFile.size<14000;
	converters = ["recoil2png", "view64"];
}
