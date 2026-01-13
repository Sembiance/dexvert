import {Format} from "../../Format.js";

export class binkEXE extends Format
{
	name           = "Bink EXE Wrapper";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["BinkEXE"];
	converters     = ["exeUnPostContent[idstring:BIKi][ext:.bik] -> dexvert[asFormat:video/bink]"];
}
