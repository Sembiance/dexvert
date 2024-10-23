import {Format} from "../../Format.js";

export class aurealAspenSoundBank extends Format
{
	name           = "Aureal Aspen sound bank";
	ext            = [".arl"];
	forbidExtMatch = true;
	magic          = ["Aureal Aspen sound bank"];
	converters     = ["awaveStudio[matchType:magic]"];
}
