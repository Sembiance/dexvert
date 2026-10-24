import {xu} from "xu";
import {Format} from "../../Format.js";

export class redSpark extends Format
{
	name         = "RedSpark";
	ext          = [".rsd"];
	magic        = ["RedSpark Audio", "GameCube RSD (rsd)", "RedSpark (redspark)", "vgmstream: redspark", "vgmstream: rsd"];
	metaProvider = ["ffprobe"];
	converters   = ["vgmstream[types:redspark,rsd]", "zxtune123", "ffmpeg[format:rsd][outType:mp3"];
}
