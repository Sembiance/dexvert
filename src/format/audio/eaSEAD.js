import {xu} from "xu";
import {Format} from "../../Format.js";

export class eaSEAD extends Format
{
	name           = "Electronic Arts Sound hEADer";
	website        = "http://fileformats.archiveteam.org/wiki/Electronic_Arts_TGV";
	ext            = [".tgv"];
	forbidExtMatch = true;
	magic          = ["Electronic Arts Sound hEADer"];
	converters     = ["vgmstream"];
}
