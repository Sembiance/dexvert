import {Format} from "../../Format.js";

export class ac3 extends Format
{
	name         = "Dolby Digital AC-3 ATSC A/52";
	website      = "https://wiki.multimedia.cx/index.php/A52";
	ext          = [".ac3"];
	magic        = ["Dolby Digital stream audio", "ATSC A/52 aka AC-3 aka Dolby Digital", /^fmt\/735( |$)/];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[outType:mp3]", "zxtune123", "vgmstream"];
}
