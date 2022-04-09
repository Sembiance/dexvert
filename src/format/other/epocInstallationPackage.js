import {Format} from "../../Format.js";

export class epocInstallationPackage extends Format
{
	name           = "EPOC Installation Package";
	ext            = [".sis"];
	forbidExtMatch = true;
	magic          = ["EPOC Installation package", "Symbian installation file"];
	converters     = ["strings"];
}
