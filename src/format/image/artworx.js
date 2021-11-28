import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class artworx extends Format
{
	name           = "ArtWorx Data Format";
	website        = "http://fileformats.archiveteam.org/wiki/ArtWorx_Data_Format";
	ext            = [".adf"];
	mimeType       = "image/x-artworx";
	magic          = [/^data$/];
	forbiddenMagic = ["Amiga Disk image File", ...TEXT_MAGIC];
	weakMagic      = true;
	metaProvider   = ["ansiArt"];
	
	// deark messes up several images, but ansilove seems to handle them all
	converters = ["ansilove[format:adf]", "deark", `abydosconvert[format:${this.mimeType}]`];
}
