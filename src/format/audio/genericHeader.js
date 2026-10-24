import {Format} from "../../Format.js";

export class genericHeader extends Format
{
	name       = "Generic Header Audio Stream";
	ext        = [".genh"];
	magic      = ["Generic Header audio stream", "GENeric Header (genh)", "vgmstream: genh"];
	converters = ["vgmstream[types:genh]", "zxtune123"];
}
