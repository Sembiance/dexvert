import {Format} from "../../Format.js";

export class andrewRasterObject extends Format
{
	name           = "Andrew Raster object";
	ext            = [".raster"];
	forbidExtMatch = true;
	magic          = ["Andrew Raster object :atk:"];
	converters     = ["nconvert[format:atk]"];
}
