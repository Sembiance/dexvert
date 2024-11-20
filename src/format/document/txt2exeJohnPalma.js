import {Format} from "../../Format.js";

export class txt2exeJohnPalma extends Format
{
	name           = "TXT2EXE (John De Palma)";
	website        = "http://fileformats.archiveteam.org/wiki/TXT2EXE.COM_(John_De_Palma)";
	ext            = [".exe", ".com"];
	forbidExtMatch = true;
	magic          = ["16bit DOS TXT2EXE (John De Palm) executable"];
	unsupported    = true;
}
