import {xu} from "xu";
import {Format} from "../../Format.js";

export class kRAWAudio extends Format
{
	name       = "kRAW Audio Stream";
	ext        = [".kraw"];
	magic      = ["kRAW Audio Stream", "Geometry Wars kRAW (kraw)"];
	converters = ["ffmpeg[libre][format:kraw][outType:mp3]", "vgmstream"];
}
