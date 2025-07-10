import {xu} from "xu";
import {Format} from "../../Format.js";

const _AVI_MAGIC = [
	// generic
	"AVI Audio Video Interleaved", /^RIFF.* data, AVI.*/, "Audio/Video Interleaved Format", "Animation Video (AVI)", "Audio Video Interleave video", "Format: AVI", "video/vnd.avi", "AVI (Audio Video Interleaved) (avi)", /^fmt\/5( |$)/,
	/^Generic RIFF file AVI $/, "deark: riff (AVI)",
	
	// specific
	/^Google Video$/
];
export {_AVI_MAGIC};

export class avi extends Format
{
	name         = "Audio Video Interleaved Video";
	website      = "http://fileformats.archiveteam.org/wiki/AVI";
	ext          = [".avi", ".divx"];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="VfW " || (macFileType==="BINA" && macFileCreator==="AVIC") || (macFileType==="AVI " && macFileCreator==="MSIE");
	mimeType     = "video/avi";
	magic        = _AVI_MAGIC;
	metaProvider = ["mplayer"];
	converters   = dexState => ["ffmpeg", "mencoderWinXP", "nihav", `xanim[fps:${dexState.meta.fps || 10}]`];
}
