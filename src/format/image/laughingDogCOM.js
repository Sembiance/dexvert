import {Format} from "../../Format.js";

export class laughingDogCOM extends Format
{
	name           = "Laughing Dog Screen Maker COM file";
	website        = "http://justsolve.archiveteam.org/wiki/Laughing_Dog_Screen_Maker_COM_file";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["Laughing Dog COM", "16bit DOS Laughing Dog Screen Maker Command", "deark: ldog_com"];
	converters     = ["deark[module:ldog_com][charOutType:image]"];
}
