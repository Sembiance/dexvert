import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class neochromeAnimation extends Format
{
	name       = "NEOchrome Animation";
	website    = "http://fileformats.archiveteam.org/wiki/NEOchrome_Animation";
	ext        = [".ani"];
	magic      = ["Atari NEOchrome animation"];
	meta       = async inputFile =>
	{
		const headerBytes = await fileUtil.readFileBytes(inputFile.absolute, 18);
		
		// Number of vblanks to delay between frames is at offset 16 (from https://temlib.org/AtariForumWiki/index.php/NEOchrome_Animation_file_format)
		const frameDelay = headerBytes.getUInt16BE(16);

		// Assume an NTSC 60Hz display, that's a 16.66ms minimum delay (+1) between frames
		return {fps : xu.SECOND/(16.66*(frameDelay+1))};
	};
	converters = dexState => [`deark -> *ffmpeg[fps:${dexState.meta.fps}]`, "deark"];
}
