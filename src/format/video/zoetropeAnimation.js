import {Format} from "../../Format.js";

export class zoetropeAnimation extends Format
{
	name           = "Zoetrope Animation";
	website        = "https://elisoftware.org/w/index.php/Zoetrope_(Amiga,_3_1/2%22_Disk)_Antic_Software_-_1988_USA,_Canada_Release";
	ext            = [".rif"];
	forbidExtMatch = true;
	magic          = ["Zoetrope animation"];
	converters     = ["vibe2avi"];
}
