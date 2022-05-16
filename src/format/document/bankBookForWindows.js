import {Format} from "../../Format.js";

export class bankBookForWindows extends Format
{
	name           = "Bank Book for Windows Account Data";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["Bank Book for Windows account Data"];
	converters     = ["strings"];
}
