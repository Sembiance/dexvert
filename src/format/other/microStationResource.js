import {Format} from "../../Format.js";

export class microStationResource extends Format
{
	name           = "MicroStation Resource Data";
	ext            = [".dat", ".ma"];
	forbidExtMatch = true;
	magic          = ["MicroStation Resource data"];
	converters     = ["strings"];
}
