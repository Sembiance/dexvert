import {Format} from "../../Format.js";

export class vgaPaint386Help extends Format
{
	name           = "VGAPaint 386 Help";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["VGAPaint 386 Help"];
	converters     = ["strings"];
}
