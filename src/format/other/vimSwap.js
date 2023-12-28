import {Format} from "../../Format.js";

export class vimSwap extends Format
{
	name           = "Vim Swap";
	website        = "http://fileformats.archiveteam.org/wiki/Vim_swap_file";
	ext            = [".swp"];
	forbidExtMatch = true;
	magic          = ["Vim swap"];
	converters     = ["strings"];
}
