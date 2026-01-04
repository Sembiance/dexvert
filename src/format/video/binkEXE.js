import {Format} from "../../Format.js";

export class binkEXE extends Format
{
	name           = "Bink EXE Wrapper";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["BinkEXE"];
	converters     = ["exe2bik -> dexvert[asFormat:video/bink]"];
}
