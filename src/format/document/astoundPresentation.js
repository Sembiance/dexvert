import {Format} from "../../Format.js";

export class astoundPresentation extends Format
{
	name           = "Astound Presentation";
	website        = "http://fileformats.archiveteam.org/wiki/Astound_Presentation";
	ext            = [".asd", ".smp", ".asv"];
	forbidExtMatch = true;
	magic          = ["Astound Presentation document"];
	unsupported    = true;
}
