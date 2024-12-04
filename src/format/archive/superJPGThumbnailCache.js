import {Format} from "../../Format.js";

export class superJPGThumbnailCache extends Format
{
	name           = "SuperJPG Thumbnail Cache";
	ext            = [".tnc"];
	forbidExtMatch = true;
	magic          = ["SuperJPG ThumbNail Cache"];
	weakMagic      = true;
	converters     = ["foremost"];
}
