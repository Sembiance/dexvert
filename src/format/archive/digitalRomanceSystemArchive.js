import {Format} from "../../Format.js";

export class digitalRomanceSystemArchive extends Format
{
	name           = "Digital Romance System Archive";
	ext            = [".dat", ".snr"];
	forbidExtMatch = true;
	magic          = ["archive:Ikura.DrsOpener"];
	converters     = ["GARbro[types:archive:Ikura.DrsOpener]"];
}
