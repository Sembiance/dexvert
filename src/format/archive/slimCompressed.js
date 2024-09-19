import {Format} from "../../Format.js";

export class slimCompressed extends Format
{
	name           = "SLIM Compressed";
	website        = "http://fileformats.archiveteam.org/wiki/SLIM_(Dominic_Herity)";
	ext            = [".exe", ".com"];
	forbidExtMatch = true;
	packed         = true;
	magic          = ["SLIM compressed"];
	converters     = ["slim"];
}
