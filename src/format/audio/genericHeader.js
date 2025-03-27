import {Format} from "../../Format.js";

export class genericHeader extends Format
{
	name       = "Generic Header Audio Stream";
	ext        = [".genh"];
	magic      = ["Generic Header audio stream", "GENeric Header (genh)"];
	converters = ["vgmstream", "zxtune123"];
}
