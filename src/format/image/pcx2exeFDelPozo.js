import {xu} from "xu";
import {Format} from "../../Format.js";

export class pcx2exeFDelPozo extends Format
{
	name           = "PCX2EXE (F. del Pozo)";
	website        = "http://fileformats.archiveteam.org/wiki/PCX2EXE_(F._del_Pozo)";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["PCX2EXE (F. del Pozo)"];
	converters     = [`dosEXEScreenshot[timeout:${xu.SECOND*10}][frameLoc:95]`];
}
