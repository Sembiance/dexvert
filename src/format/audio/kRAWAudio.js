import {xu} from "xu";
import {Format} from "../../Format.js";

export class kRAWAudio extends Format
{
	name       = "kRAW Audio Stream";
	ext        = [".kraw"];
	magic      = ["kRAW Audio Stream"];
	converters = ["vgmstream"];
}
