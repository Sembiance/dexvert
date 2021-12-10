import {xu} from "xu";
import {Format} from "../../Format.js";

export class viacomNewMedia extends Format
{
	name        = "Viacom New Media Sprite Archive";
	website     = "http://www.shikadi.net/moddingwiki/Viacom_New_Media_Graphics_File_Format";
	ext         = [".vnm", ".000"];
	magic       = ["Viacom New Media graphics"];
	unsupported = true;
	notes       = xu.trim`
		An obscure format that packs multiple bitmaps and sprites into a single archive. Found the following two projects that extract them:
		https://github.com/jmcclell/vnmgf-exporter
		Sadly neither one can correctly process/extract the VNM files I encountered. The github link is much closer and is in modern Go.`;
}
