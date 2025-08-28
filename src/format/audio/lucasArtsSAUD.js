import {xu} from "xu";
import {Format} from "../../Format.js";

export class lucasArtsSAUD extends Format
{
	name       = "LucasArts SAUD";
	ext        = [".sad"];
	forbidExtMatch = true;
	magic      = ["LucasArts SAUD (saud)"];
	converters = ["ffmpeg[libre][format:saud][outType:mp3]"];
}
