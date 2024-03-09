import {Format} from "../../Format.js";

export class cinema4D extends Format
{
	name        = "Cinema 4D";
	website     = "http://fileformats.archiveteam.org/wiki/C4D";
	ext         = [".c4d", ".mc4d"];
	magic       = ["IFF Cinema 4D file", "IFF data, MC4D MaxonCinema4D rendering", "Maxon Cinema 4D scene", "CINEMA 4D model", "Cinema 4D XML", /^fmt\/(415|1180)( |$)/];
	unsupported = true;
}
