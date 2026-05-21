import {Format} from "../../Format.js";

export class infiniDScene extends Format
{
	name        = "Infini-D Scene";
	website     = "http://fileformats.archiveteam.org/wiki/Infini-D";
	ext         = [".ids", ".id4"];
	magic       = ["Infini-D Scene File", "Infini-D scene"];
	unsupported = true;	// only 494 unique files on discmaster, and these scene files are small, so I'm thinking maybe they just contain scene info and no actual models/textures
}
