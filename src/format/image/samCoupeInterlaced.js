import {Format} from "../../Format.js";

export class samCoupeInterlaced extends Format
{
	name       = "SAM Coupe Interlaced";
	ext        = [".lce"];
	fileSize   = [49234];
	converters = ["recoil2png"];
}
