import {xu} from "xu";
import {Format} from "../../Format.js";

const _AVI_MAGIC = [
	// generic
	"AVI Audio Video Interleaved", /^RIFF.* data, AVI.*/, "Audio/Video Interleaved Format", "Animation Video (AVI)", "Audio Video Interleave video", "Format: AVI", "video/vnd.avi", "AVI (Audio Video Interleaved) (avi)", /^fmt\/5( |$)/,
	
	// specific
	/^Google Video$/
];
export {_AVI_MAGIC};

export class avi extends Format
{
	name     = "Audio Video Interleaved Video";
	website  = "http://fileformats.archiveteam.org/wiki/AVI";
	ext      = [".avi", ".divx"];
	idMeta   = ({macFileType}) => macFileType==="VfW ";
	mimeType = "video/avi";

	// The 'entertainment utility' CDs have AVI files and a corresponding TSS file 308303 bytes long. Thought maybe a converter could use it to help, but doesn't seem to do anything
	//keepFilename  : true,
	//filesOptional : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.tss`),

	magic        = _AVI_MAGIC;
	metaProvider = ["mplayer"];
	slow         = true;
	converters   = r => ["ffmpeg", "mencoderWinXP", `xanim[fps:${r.meta.fps || 10}]`];
}
