import {Format} from "../../Format.js";

export class cyberStudioCAD3D extends Format
{
	name        = "Cyber Studio/CAD-3D";
	website     = "http://fileformats.archiveteam.org/wiki/CAD-3D";
	ext         = [".3d2", ".3d"];
	magic       = ["Cyber Studio CAD-3D", "CAD-3D object"];
	unsupported = true;
	notes       = "Original program was Atari ST and later 'Cyber' version is pretty rare and not sure if there is a 'windows' version. Couldn't find a converter.";
}
