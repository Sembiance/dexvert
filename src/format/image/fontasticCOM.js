import {xu} from "xu";
import {Format} from "../../Format.js";

export class fontasticCOM extends Format
{
	name           = "Fontastic .COM File";
	website        = "http://fileformats.archiveteam.org/wiki/Fontastic_COM_format";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["16bit DOS Fontastic screen loader Command"];
	converters     = [`dosEXEScreenshot[timeout:${xu.SECOND*15}][frameLoc:95]`];
}
