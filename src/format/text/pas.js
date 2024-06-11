import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class pas extends Format
{
	name           = "Pascal/Delphi Source File";
	website        = "http://fileformats.archiveteam.org/wiki/Pascal";
	ext            = [".pas", ".tp5"];
	forbidExtMatch = true;
	magic          = [...TEXT_MAGIC, "Delphi Project source", "Pascal Programm", "Pascal Source Code 'DOS'"];	// double trailing mm is not a typo, it's from gt2
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
