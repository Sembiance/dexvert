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
}
