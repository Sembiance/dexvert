import {xu} from "xu";
import {Format} from "../../Format.js";

export class eaSEAD extends Format
{
	name           = "Electronic Arts Sound hEADer";
	ext            = [".tgv"];
	forbidExtMatch = true;
	magic          = ["Electronic Arts Sound hEADer"];
	converters     = ["vgmstream"];
}
