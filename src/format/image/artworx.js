import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class artworx extends Format
{
	name           = "ArtWorx Data Format";
	website        = "http://fileformats.archiveteam.org/wiki/ArtWorx_Data_Format";
	ext            = [".adf"];
	mimeType       = "image/x-artworx";
	magic          = [/^data$/];
	forbiddenMagic = ["Amiga Disk image File", "AppleDouble encoded Macintosh file", "Mac AppleDouble encoded", ...TEXT_MAGIC];
	weakMagic      = true;
	metaProvider   = ["ansiloveInfo", "ffprobe"];
	
	// .adf can be somewhat common of an image format, so only convert if we have a formatName from ffprobe
	// ansilove and ffmpeg both do great. deark messes up several images
	converters = r => (r.meta?.formatName==="adf" ? ["ansilove[format:adf]", "ffmpeg[format:adf][outType:png]", "deark[module:artworx_adf]", `abydosconvert[format:${this.mimeType}]`] : []);
}
