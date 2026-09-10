import {Format} from "../../Format.js";

export class andrewRasterObject extends Format
{
	name           = "Andrew Raster object";
	ext            = [".raster"];
	forbidExtMatch = true;
	magic          = ["Andrew Raster object :atk:", "Andrew Toolkit raster image data"];
	converters     = ["nconvert[format:atk]"];
}
