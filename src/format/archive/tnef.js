import {Format} from "../../Format.js";

export class tnef extends Format
{
	name           = "Transport Neutral Encapsulation Format";
	website        = "http://fileformats.archiveteam.org/wiki/Transport_Neutral_Encapsulation_Format";
	ext            = [".tnef", ".dat"];
	forbidExtMatch = [".dat"];
	magic          = ["Transport Neutral Encapsulation Format", "TNEF"];
	converters     = ["ytnef"];
}
