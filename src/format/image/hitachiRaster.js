import {Format} from "../../Format.js";

export class hitachiRaster extends Format
{
	name           = "Hitachi Raster Format bitmap";
	ext            = [".hrf"];
	forbidExtMatch = true;
	magic          = ["Hitachi Raster Format bitmap"];
	converters     = ["imageAlchemy"];
	unsupported    = true;	// could not locate any working sample files
}
