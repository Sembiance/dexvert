import {xu} from "xu";
import {Format} from "../../Format.js";

export class redSpark extends Format
{
	name       = "RedSpark";
	ext        = [".rsd"];
	magic      = ["RedSpark Audio"];
	converters = ["vgmstream", "zxtune123", "ffmpeg[format:rsd][outType:mp3"];
}