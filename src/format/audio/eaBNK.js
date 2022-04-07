import {xu} from "xu";
import {Format} from "../../Format.js";

export class eaBNK extends Format
{
	name           = "Electronic Arts BNK File";
	ext            = [".bnk"];
	forbidExtMatch = true;
	magic          = ["EA BNK Audio"];
	converters     = ["vgmstream"];
}
