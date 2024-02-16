import {Format} from "../../Format.js";

export class pc98FAT12 extends Format
{
	name           = "PC-98 FAT12";
	ext            = [".hdi", ".fdd", ".fdi"];
	forbidExtMatch = true;
	magic          = ["PC-98 FAT12"];
	converters     = ["pc98ripper"];
}
