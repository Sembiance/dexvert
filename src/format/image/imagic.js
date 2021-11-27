import {Format} from "../../Format.js";

export class imagic extends Format
{
	name       = "Imagic";
	website    = "http://fileformats.archiveteam.org/wiki/Imagic_Film/Picture";
	ext        = [".ic1", ".ic2", ".ic3"];
	magic      = ["Imagic picture/animation bitmap"];
	converters = ["recoil2png"]
}
