import {Format} from "../../Format.js";

export class duneGraph extends Format
{
	name       = "DuneGraph";
	website    = "http://fileformats.archiveteam.org/wiki/DuneGraph";
	ext        = [".dc1", ".dg1"];
	magic      = ["DuneGraph Compressed bitmap", "DuneGraph Compressed bitma", "DuneGraph Uncompressed bitmap"];
	converters = ["recoil2png[format:DG1,DC1]"];
}
