import {xu} from "xu";
import {Format} from "../../Format.js";

export class digitalRomanceSystemArchive extends Format
{
	name           = "Digital Romance System Archive";
	ext            = [".dat", ".snr"];
	forbidExtMatch = true;
	magic          = ["archive:Ikura.DrsOpener"];
	idCheck        = inputFile => inputFile.size>xu.KB*4;
	converters     = ["GARbro[types:archive:Ikura.DrsOpener]"];
}
