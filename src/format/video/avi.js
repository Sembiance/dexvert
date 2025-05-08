import {xu} from "xu";
import {Format} from "../../Format.js";

const _AVI_MAGIC = [
	// generic
	"AVI Audio Video Interleaved", /^RIFF.* data, AVI.*/, "Audio/Video Interleaved Format", "Animation Video (AVI)", "Audio Video Interleave video", "Format: AVI", "video/vnd.avi", "AVI (Audio Video Interleaved) (avi)", /^fmt\/5( |$)/,
	/^Generic RIFF file AVI $/,
	
	// specific
	/^Google Video$/
];
export {_AVI_MAGIC};

export class avi extends Format
{
	name         = "Audio Video Interleaved Video";
	website      = "http://fileformats.archiveteam.org/wiki/AVI";
	ext          = [".avi", ".divx"];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="VfW " || (macFileType==="BINA" && macFileCreator==="AVIC");
	mimeType     = "video/avi";
	magic        = _AVI_MAGIC;
	metaProvider = ["mplayer"];
	slow         = true;
	converters   = r => ["ffmpeg", "mencoderWinXP", "nihav", `xanim[fps:${r.meta.fps || 10}]`];
}
