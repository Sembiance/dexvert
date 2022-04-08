import {Format} from "../../Format.js";

export class psion3Word extends Format
{
	name           = "Psion Series 3 Word Document";
	website        = "http://fileformats.archiveteam.org/wiki/Psion_Series_3_Word";
	ext            = [".wrd"];
	forbidExtMatch = true;
	magic          = ["Psion serie 3 word document"];
	converters     = ["strings"];
}
