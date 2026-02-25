import {Format} from "../../Format.js";

export class houseOfTheDeadTextures extends Format
{
	name           = "The House of the Dead textures";
	ext            = [".vmc", ".vram"];
	forbidExtMatch = true;
	magic          = ["The House of the Dead textures"];
	converters     = ["wuimg[format:vvtp]"];
}
