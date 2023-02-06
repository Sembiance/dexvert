import {Format} from "../../Format.js";

export class mrSIDImage extends Format
{
	name           = "Multi-resolution Seamless Image Database";
	website        = "http://fileformats.archiveteam.org/wiki/MrSID";
	ext            = [".sid"];
	forbidExtMatch = true;
	magic          = ["LizardTech MrSID photo"];
	converters     = ["mrsiddecode"];
}
