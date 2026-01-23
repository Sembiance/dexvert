import {Format} from "../../Format.js";

export class aurealAspenSoundBank extends Format
{
	name           = "Aureal Aspen sound bank";
	ext            = [".arl"];
	forbidExtMatch = true;
	magic          = ["Aureal Aspen sound bank"];
	forbiddenMagic = ["Emu Sound Font (v1.0)"];
	converters     = ["awaveStudio"];
}
