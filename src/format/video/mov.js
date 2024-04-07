import {Format} from "../../Format.js";

const _MOV_MAGIC = ["Apple QuickTime movie", "QuickTime Movie", "Mac QuickTime video", "ISO Media, Apple QuickTime movie", "Apple QuickTime Film", /^MacBinary II.+'MooV'/, /^x-fmt\/384( |$)/];
const _MOV_EXT = [".mov", ".omv", ".pmv", ".qt"];
export {_MOV_MAGIC, _MOV_EXT};

export class mov extends Format
{
	name         = "Apple QuickTime movie";
	website      = "http://fileformats.archiveteam.org/wiki/QuickTime";
	ext          = _MOV_EXT;
	mimeType     = "video/quicktime";
	magic        = _MOV_MAGIC;
	idMeta      = ({macFileType}) => macFileType==="MooV";
	trustMagic   = true;
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg", "qt_flatt", "mencoderWinXP", "quickTimePlayer", "corelPhotoPaint[outType:avi]", "xanim"];
}
