import {Format} from "../../Format.js";

export class swagPacket extends Format
{
	name       = "SWAG Packet";
	website    = "http://fileformats.archiveteam.org/wiki/SWG";
	ext        = [".swg"];
	magic      = ["Swag archive data", "Swag Reader Packet", "SWAG Archiv gefunden", "SWAG packet", "deark: swg (SWAG packet)"];
	converters = ["swagReader"];
}
