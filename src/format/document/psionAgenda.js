import {Format} from "../../Format.js";

export class psionAgenda extends Format
{
	name           = "Psion Agenda";
	ext            = [".agn"];
	forbidExtMatch = true;
	magic          = ["Psion S3a/3c/Siena Agenda"];
	converters     = ["strings"];
}
