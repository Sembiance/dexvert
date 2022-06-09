import {Format} from "../../Format.js";

export class verityCollectionIndexDescriptor extends Format
{
	name           = "Verity Collection Index Descriptor";
	ext            = [".wld", ".ddd", ".did", ".pdd", ".rsd"];
	forbidExtMatch = true;
	magic          = ["Verity Collection Index Descriptor"];
	weakMagic      = true;
	converters     = ["strings"];
}
