import {Format} from "../../Format.js";

export class txt2exePFischer extends Format
{
	name           = "TXT2EXE (P. Fischer-Haaser)";
	website        = "http://fileformats.archiveteam.org/wiki/TXT2EXE_(P._Fischer-Haaser)";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["16bit DOS TXT2EXE (P.Fischer-Haaser)"];
	unsupported    = true;
}
