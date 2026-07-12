import {Format} from "../../Format.js";

export class aolSetup extends Format
{
	name           = "AOLSetup Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: AOLSetup"];
	converters     = ["vibeExtract"];
}
