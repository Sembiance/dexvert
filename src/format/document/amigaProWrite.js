import {Format} from "../../Format.js";

export class amigaProWrite extends Format
{
	name           = "Amiga ProWrite Document";
	magic          = ["Amiga ProWrite document", "IFF data, ProWrite document"];
	converters     = ["strings"];
}
