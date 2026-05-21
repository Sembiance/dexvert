import {Format} from "../../Format.js";

export class polyfilm extends Format
{
	name        = "Polyfilm 3D Model";
	ext         = [".3d"];
	magic       = ["Polyfilm 3D model"];
	unsupported = true;	// only 21 unique files on discmaster (Atari ST program)
}
