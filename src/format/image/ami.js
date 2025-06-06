import {Format} from "../../Format.js";

export class ami extends Format
{
	name           = "Amica Paint";
	website        = "http://fileformats.archiveteam.org/wiki/Amica_Paint";
	ext            = [".ami"];
	forbidExtMatch = true;
	magic          = ["Amica Paint :ami:"];
	idCheck        = inputFile => inputFile.size>1000 && inputFile.size<14000;
	converters     = ["recoil2png", "nconvert[format:ami]", "view64"];
}
