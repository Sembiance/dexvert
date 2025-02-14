import {Format} from "../../Format.js";

export class signumDocument3 extends Format
{
	name           = "Signum Document v3";
	ext            = [".sdk"];
	forbidExtMatch = true;
	magic          = ["Signum 3/4 Document"];
	unsupported    = true;
}
