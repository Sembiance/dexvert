import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class povRay extends Format
{
	name        = "POV-Ray Scene";
	website     = "http://fileformats.archiveteam.org/wiki/POV-Ray_scene_description";
	ext         = [".pov"];
	magic       = TEXT_MAGIC;
	weakMagic   = true;
	unsupported = true;
	notes       = `
		POV Ray is not backwards compatible with old versions. So v1.0 files need to ran with 1.0. Old versions available from: http://www.povray.org/ftp/pub/povray/Old-Versions/
		So I'd need to try most recent (system installed version) to oldest until one works
		I have compiled povray1 as dexvert/bin/povray/povray1
		Additionally povray files can include pointers to files in other directories so I'd have to go 'fetch' them and bring them into the same directory
		Next, includes are 'case sensitive' but originally on things like DOS, they were not, so I'd need to ensure the included files and include directives have the same case
		POVRAY1 also generates broken TGA output that only seem to convert with nconvert
		Lastly, it would be ideal to convert to a modern 3D/scene format as part of the 'poly' improvement phase`;
}
