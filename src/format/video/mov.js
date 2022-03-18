import {Format} from "../../Format.js";

const _MOV_MAGIC = ["Apple QuickTime movie", "QuickTime Movie", "Mac QuickTime video", /^MacBinary II.+'MooV'/];
const _MOV_EXT = [".mov", ".omv", ".pmv", ".qt"];
export {_MOV_MAGIC, _MOV_EXT};

export class mov extends Format
{
	name         = "Apple QuickTime movie";
	website      = "http://fileformats.archiveteam.org/wiki/MOV";
	ext          = _MOV_EXT;
	mimeType     = "video/quicktime";
	magic        = _MOV_MAGIC;
	trustMagic   = true;
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg", "xanim", "qt_flatt", "mencoderWinXP"];
}
