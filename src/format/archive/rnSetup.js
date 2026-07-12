import {Format} from "../../Format.js";

export class rnSetup extends Format
{
	name           = "RNSetup Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: RNsetup"];
	converters     = ["vibeExtract"];
}
