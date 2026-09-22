import {Format} from "../../Format.js";

export class favoritePointResource extends Format
{
	name           = "Favorite Point Resource Archive";
	ext            = [".bin"];
	forbidExtMatch = true;
	magic          = ["archive:FVP.Bin2Opener"];
	converters     = ["GARbro[types:archive:FVP.Bin2Opener]"];
}
