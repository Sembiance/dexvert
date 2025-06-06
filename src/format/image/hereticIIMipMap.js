import {Format} from "../../Format.js";

export class hereticIIMipMap extends Format
{
	name       = "Heretic II MipMap";
	ext        = [".m8"];
	magic      = ["Heretic II MipMap :m8:"];
	converters = ["nconvert[format:m8]"];
}
