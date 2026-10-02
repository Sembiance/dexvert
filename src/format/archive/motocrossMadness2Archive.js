import {Format} from "../../Format.js";

export class motocrossMadness2Archive extends Format
{
	name           = "Motocross Madness 2 archive";
	ext            = [".dat", ".text"];
	forbidExtMatch = true;
	magic          = [/^geArchive: TEX_RS2( |$)/];
	converters     = ["gameextractor[codes:TEX_RS2]"];
}
