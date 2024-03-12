import {Format} from "../../Format.js";

export class polyfilm extends Format
{
	name        = "Polyfilm 3D Model";
	ext         = [".3d"];
	magic       = ["Polyfilm 3D model"];
	unsupported = true;
	notes       = "Only 21 unique files on discmaster, all look to be example files from an Atari ST program called Polyfilm.";
}
