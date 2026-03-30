import {xu} from "xu";
import {Format} from "../../Format.js";

export class viacomNewMedia extends Format
{
	name           = "Viacom New Media Sprite Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/Viacom_New_Media_Graphics_File_Format";
	ext            = [".vnm", ".000"];
	forbidExtMatch = true;
	magic          = ["Viacom New Media graphics", /^fmt\/1610( |$)/];
	converters     = ["unViacomNewMedia"];
}
