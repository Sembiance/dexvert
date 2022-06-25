import {Format} from "../../Format.js";

export class vimSwap extends Format
{
	name           = "Vim Swap";
	ext            = [".swp"];
	forbidExtMatch = true;
	magic          = ["Vim swap"];
	converters     = ["strings"];
}
