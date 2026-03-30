import {Format} from "../../Format.js";

export class setupMVA extends Format
{
	name           = "Setup Program Archive";
	ext            = [".mva", ".mvb"];
	forbidExtMatch = true;
	magic          = ["Setup Program Archive", "Archive: MVA"];
	converters     = ["unSetupMVA"];
}
