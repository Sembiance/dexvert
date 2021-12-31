import {xu} from "xu";
import {Format} from "../../Format.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class binaryText extends Format
{
	name           = "Binary Text";
	website        = "http://fileformats.archiveteam.org/wiki/BIN_(Binary_Text)";
	ext            = [".bin"];
	mimeType       = "text/x-binary";
	forbiddenMagic = TEXT_MAGIC_STRONG;
	notes          = "It's crazy hard to identify this file, and we err on the side of caution. So we only convert files that have meta data set in them.";
	metaProvider   = ["ansiArt", "ffprobe"];
	idCheck        = inputFile => inputFile.size<=xu.MB*2;	// .bin is so generic, only try converting if less than 2MB, otherwise it's unlikely to be this format

	// Only convert if ffprobe found the proper formatName. NOTE, this causes some files not to be detected, such as 'r5-XVOL1.BIN' but the flip side is in the wild tons of .bin files get mistaken for Binary Text and converted to garbage
	converters = r => (r.meta?.formatName==="bin" ? ["deark[module:bintext][charOutType:image]", "ansilove[format:bin]", `abydosconvert[format:${this.mimeType}]`, "ffmpeg[codec:bintext][outType:png]"] : []);
}
