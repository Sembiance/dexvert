import {Format} from "../../Format.js";

export class laughingDogCOM extends Format
{
	name           = "Laughing Dog Screen Maker COM file";
	website        = "http://justsolve.archiveteam.org/wiki/Laughing_Dog_Screen_Maker_COM_file";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["Laughing Dog COM"];
	converters     = ["deark[module:ldog_com][charOutType:image]"];
}
