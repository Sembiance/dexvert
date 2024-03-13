import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class animaticFilm extends Format
{
	name       = "Animatic Film";
	website    = "http://fileformats.archiveteam.org/wiki/Animatic_Film";
	ext        = [".flm"];
	magic      = ["Animatic Film", /^fmt\/1784( |$)/];
	meta       = async inputFile =>
	{
		const headerBytes = await fileUtil.readFileBytes(inputFile.absolute, 36);
		
		// Number of vblanks to delay is 99 - offset 34 (from https://temlib.org/AtariForumWiki/index.php/Animatic_Film_file_format)
		const frameDelay = (99-headerBytes.getUInt16BE(34));

		// Assume an NTSC 60Hz display, that's a 16.66ms minimum delay (+1) between frames
		return {fps : xu.SECOND/(16.66*(frameDelay+1))};
	};
	converters = dexState => [`deark[module:animatic] -> *ffmpeg[fps:${dexState.meta.fps}]`, "deark[module:animatic]"];
}
