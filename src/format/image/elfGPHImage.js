import {Format} from "../../Format.js";

export class elfGPHImage extends Format
{
	name           = "Elf GPH Image";
	ext            = [".gph"];
	forbidExtMatch = true;
	magic          = ["image:Elf.GphFormat"];
	converters     = ["GARbro[types:image:Elf.GphFormat]"];
}
