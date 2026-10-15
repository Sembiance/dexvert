import {Format} from "../../Format.js";

export class ancientElfArchive extends Format
{
	name           = "Ancient Elf Archive";
	ext            = [".vol"];
	forbidExtMatch = true;
	magic          = ["archive:Elf.VolOpener"];
	converters     = ["GARbro[types:archive:Elf.VolOpener]"];
}
