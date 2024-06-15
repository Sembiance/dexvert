import {Format} from "../../Format.js";

export class hpack extends Format
{
	name       = "HPACK Archive";
	website    = "http://fileformats.archiveteam.org/wiki/HPACK_(compressed_archive)";
	ext        = [".hpk"];
	magic      = ["HPack archive data", "HPACK archive data", "HPACK compressed archive"];
	converters = ["hpack"];
}
