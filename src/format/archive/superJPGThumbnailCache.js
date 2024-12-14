import {Format} from "../../Format.js";

export class superJPGThumbnailCache extends Format
{
	name           = "SuperJPG Thumbnail Cache";
	website        = "http://fileformats.archiveteam.org/wiki/SuperJPG_thumbnail_cache";
	ext            = [".tnc"];
	forbidExtMatch = true;
	magic          = ["SuperJPG ThumbNail Cache"];
	weakMagic      = true;
	converters     = ["foremost"];
}
