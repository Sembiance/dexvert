import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class binaryText extends Format
{
	name           = "Binary Text";
	website        = "http://fileformats.archiveteam.org/wiki/BIN_(Binary_Text)";
	ext            = [".bin"];
	mimeType       = "text/x-binary";
	forbiddenMagic = TEXT_MAGIC;
	notes          = "It's crazy hard to identify this file, and we err on the side of caution. So we only convert files that have meta data set in them.";
	metaProvider   = ["ansiArt", "ffprobe"];

	converters = r => (Object.keys(r.meta).length>0 ? ["deark[module:bintext][charOutType:image]", "ansilove[format:bin]", `abydosconvert[format:${this.mimeType}]`, "ffmpeg[codec:bintext][outType:png]"] : []);
}
