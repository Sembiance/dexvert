import {Format} from "../../Format.js";

export class ibmKIPS extends Format
{
	name       = "IBM KIPS Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/IBM_KIPS_bitmap";
	ext        = [".kps"];
	magic      = ["IBM KIPS bitmap"];
	converters = ["nconvert"];
}
