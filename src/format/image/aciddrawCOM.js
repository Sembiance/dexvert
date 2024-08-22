import {xu} from "xu";
import {Format} from "../../Format.js";

export class aciddrawCOM extends Format
{
	name           = "ACiDDraw COM";
	website        = "http://fileformats.archiveteam.org/wiki/ACiDDraw_COM_file";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["ACiDDraw COM"];
	converters     = ["deark[module:aciddraw_com][charOutType:image]"];
}
