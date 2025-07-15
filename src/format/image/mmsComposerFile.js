import {Format} from "../../Format.js";

export class mmsComposerFile extends Format
{
	name           = "MMS Composer File";
	ext            = [".mcf"];
	forbidExtMatch = true;
	magic          = ["MMS Composer File"];
	weakMagic      = true;
	converters     = ["foremost"];	// don't really know what this file is, but the one sample I have has a PNG in it
}
