import {xu} from "xu";
import {Format} from "../../Format.js";

export class avi extends Format
{
	name     = "Audio Video Interleaved Video";
	website  = "http://fileformats.archiveteam.org/wiki/AVI";
	ext      = [".avi"];
	mimeType = "video/avi";

	// The 'entertainment utility' CDs have AVI files and a corresponding TSS file 308303 bytes long. Thought maybe a converter could use it to help, but doesn't seem to do anything
	//keepFilename  : true,
	//filesOptional : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.tss`),

	magic        = ["AVI Audio Video Interleaved", /^RIFF.* data, AVI.* video/, "Audio/Video Interleaved Format"];
	converters   = r => ["ffmpeg", `xanim[fps:${r.meta.fps || 10}]`];
	metaProvider = ["mplayer"];
}
