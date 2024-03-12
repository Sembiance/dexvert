import {Format} from "../../Format.js";

export class electricImage3DFile extends Format
{
	name       = "Electric Image 3D File";
	website    = "http://fileformats.archiveteam.org/wiki/FACT";
	ext        = [".fact", ".fac"];
	magic      = ["ElectricImage 3D file"];
	converters = ["i3DConverter"];
}
