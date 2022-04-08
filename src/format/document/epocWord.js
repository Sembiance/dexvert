import {Format} from "../../Format.js";

export class epocWord extends Format
{
	name           = "Psion Series 3 Word Document";
	website        = "http://fileformats.archiveteam.org/wiki/EPOC_Word";
	ext            = [".wrd", ".psi"];
	forbidExtMatch = true;
	magic          = ["Psion Series 5 Word file", "EPOC Word document", "Psion Serie 5/EPOC Word document"];
	converters     = ["psiconv"];
}
