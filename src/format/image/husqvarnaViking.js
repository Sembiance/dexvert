import {xu} from "xu";
import {Format} from "../../Format.js";

export class husqvarnaViking extends Format
{
	name           = "Husqvarna Viking Embroidery";
	website        = "http://fileformats.archiveteam.org/wiki/HUS";
	ext            = [".hus"];
	forbidExtMatch = true;
	magic          = ["Husqvarna Viking embroidery format", /^fmt\/2000( |$)/];
	converters     = ["konvertor"];
}
