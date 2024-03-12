import {xu} from "xu";
import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class povRay extends Format
{
	name      = "POV-Ray Scene";
	website   = "http://fileformats.archiveteam.org/wiki/POV-Ray_scene_description";
	ext       = [".pov"];
	magic     = TEXT_MAGIC;
	weakMagic = true;
	auxFiles  = (input, otherFiles) =>
	{
		const supportFiles = otherFiles.filter(o => [".inc"].includes(o.ext.toLowerCase()));	// we really need to actually parse the entire POV ray and go 'hunting' for all requirements, includes and images, etc
		return supportFiles.length===0 ? false : supportFiles;
	};
	keepFilename = true;
	unsupported  = true;
	notes        = xu.trim`
		POV Ray is not backwards compatible with old versions. So v1.0 files need to ran with 1.0. Old versions available from: http://www.povray.org/ftp/pub/povray/Old-Versions/
		So I'd need to detect the version of the file and use that, or try most recent (system installed version) and proceed backwards to oldest
		I have compiled povray1 as dexvert/bin/povray/povray1
		Additionally povray files can include pointers to files in other directories so I'd have to go 'fetch' them and bring them into the same directory
		These are both 'includes' and pointers to images.
		Next, includes are 'case sensitive' but originally on things like DOS, they were not, so I'd need to ensure the included files and include directives have the same case
		POVRAY1 also generates broken TGA output that only seems to convert with nconvert
		Lastly, I'm not sure how to get it as a poly. My hunch is Pov Ray 1.0 (and maybe later versions too) really are just a 'renderer' and don't have any way to export to another 3D model format.
		assimp claims support for PovRAY Raw (.raw) and AccuTrans3D says it supports .pov but a few gentle tests on my part yielded no results`;
}
