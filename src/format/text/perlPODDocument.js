import {Format} from "../../Format.js";

export class perlPODDocument extends Format
{
	name           = "Perl POD Document";
	ext            = [".pm"];
	forbidExtMatch = true;
	magic          = ["Perl POD document"];
	untouched      = true;
	metaProvider   = ["text"];
}
