import {Format} from "../../Format.js";

export class erdasLANGIS extends Format
{
	name       = "ERDAS LAN/GIS";
	website    = "http://fileformats.archiveteam.org/wiki/ERDAS_LAN/GIS";
	ext        = [".lan", ".gis"];
	magic      = ["ERDAS Image bitmap"];
	converters = ["imageAlchemy"];
}
