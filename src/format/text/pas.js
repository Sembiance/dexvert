import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class pas extends Format
{
	name           = "Pascal/Delphi Source File";
	website        = "http://fileformats.archiveteam.org/wiki/Pascal";
	ext            = [".pas", ".tp5"];
	forbidExtMatch = true;
	magic          = [...TEXT_MAGIC, "Delphi Project source"];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
