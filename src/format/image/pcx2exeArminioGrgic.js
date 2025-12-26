import {xu} from "xu";
import {Format} from "../../Format.js";

export class pcx2exeArminioGrgic extends Format
{
	name           = "PCX2EXE (Arminio Grgic)";
	website        = "http://fileformats.archiveteam.org/wiki/PCX2EXE_(Arminio_Grgic)";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["16bit DOS PCX2EXE (Arminio Grgic)", "PCX2EXE (Arminio Grgic)"];
	converters     = [`dosEXEScreenshot[timeout:${xu.SECOND*10}][frameLoc:95]`];
}
