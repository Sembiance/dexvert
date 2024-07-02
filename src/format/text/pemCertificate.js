import {Format} from "../../Format.js";

export class pemCertificate extends Format
{
	name           = "PEM Certificate";
	ext            = [".cer"];
	forbidExtMatch = true;
	magic          = ["PEM certificate", "Internet Security Certificate"];
	untouched      = true;
	metaProvider   = ["text"];
}
