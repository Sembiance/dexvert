import {Format} from "../../Format.js";

export class amiga16vx extends Format
{
	name        = "Amiga 16VX Sound";
	magic       = ["IFF data, 16SV", "Amiga IFF 16SVX Audio"];
	unsupported = true;
}
