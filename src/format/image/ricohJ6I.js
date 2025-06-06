import {Format} from "../../Format.js";

export class ricohJ6I extends Format
{
	name       = "Ricoh JSI Image";
	website    = "http://justsolve.archiveteam.org/wiki/J6I";
	ext        = [".j6i"];
	magic      = ["Ricoh digital camera image", "Ricoh Digital Camera :j6i:"];
	converters = ["nconvert[format:j6i]"];
}
