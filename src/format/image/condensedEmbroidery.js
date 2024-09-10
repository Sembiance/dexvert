import {xu} from "xu";
import {Format} from "../../Format.js";

export class condensedEmbroidery extends Format
{
	name           = "Condensed embroidery format";
	ext            = [".cnd"];
	forbidExtMatch = true;
	magic          = ["cnd/Dos Condensed embroidery format"];
	unsupported    = true;
}
