import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class videoMasterFilm extends Format
{
	name       = "Video Master Film";
	website    = "http://fileformats.archiveteam.org/wiki/Video_Master_Film";
	ext        = [".flm", ".vid", ".vsq"];
	magic      = ["Video Master Film"];
	meta       = async inputFile =>
	{
		const headerBytes = await fileUtil.readFileBytes(inputFile.absolute, 10);
		const playbackRate = headerBytes.getUInt16BE(8);

		// Frame rate table from: http://fileformats.archiveteam.org/wiki/Video_Master_Film
		return {fps : [30, 15, 10, 7, 5, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8, 9][playbackRate>15 ? 2 : playbackRate]};
	};
	converters = dexState => [`deark -> *ffmpeg[fps:${dexState.meta.fps}]`];
}
