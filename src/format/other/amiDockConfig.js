import {Format} from "../../Format.js";

export class amiDockConfig extends Format
{
	name           = "AmiDock Configuration";
	ext            = [".config"];
	forbidExtMatch = true;
	magic          = ["AmiDock Configuration"];
	weakMagic      = true;
	converters     = ["strings"];
}
