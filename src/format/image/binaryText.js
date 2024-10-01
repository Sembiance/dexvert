import {xu} from "xu";
import {Format} from "../../Format.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class binaryText extends Format
{
	name           = "Binary Text";
	website        = "http://fileformats.archiveteam.org/wiki/BIN_(Binary_Text)";
	ext            = [".bin"];
	magic          = ["Binary text (bin)"];
	weakMagic      = true;
	fallback       = true;
	mimeType       = "text/x-binary";
	forbiddenMagic = TEXT_MAGIC_STRONG;
	notes          = xu.trim`
		It's crazy hard to identify this file as it's just RAW PC screen memory.
		So we only convert files that are identified as binary text by ffprobe, even though it identifies random .bin files as bin format.
		Since all the converters will happily convert garbage, we end up with a lot of random .bin files being converted as garbage.
		So we set it as a fallback, so it's handled dead last.
		We also only convert if the file is between 4,000 and 400,000 bytes as I haven't encountered any binary text files larger than 360k.
		Even with all these restrictions we will likely convert lots of random .bin files into garbage, but there isn't much of an alternative.`;
	metaProvider   = ["ansiloveInfo", "ffprobe"];
	idCheck        = inputFile => inputFile.size>=4000 && inputFile.size<=400_000;	// .bin is so generic, only try converting if less than 400k, otherwise it's unlikely to be this format

	// Only convert if ffprobe or ansiloveInfo found the proper formatName
	converters = r => ((r.meta?.id?.startsWith("SAUCE") || r.meta?.formatName==="bin") ? ["deark[module:bintext][charOutType:image]", "ansilove[format:bin]", `abydosconvert[format:${this.mimeType}]`, "ffmpeg[codec:bintext][outType:png]"] : []);
	classify   = true;
}
