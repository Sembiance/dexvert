import {Format} from "../../Format.js";

export class dr2d extends Format
{
	name       = "DR2D Image";
	website    = "http://fileformats.archiveteam.org/wiki/DR2D";
	ext        = [".dr2d"];
	magic      = ["IFF data, DR2D 2-D object", "IFF 2-D Object standard format"];
	converters = ["DR2DtoPS"];
}
