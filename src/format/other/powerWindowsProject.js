import {Format} from "../../Format.js";

export class powerWindowsProject extends Format
{
	name           = "PowerWindows Project";
	ext            = [".pw"];
	forbidExtMatch = true;
	magic          = ["PowerWindows Project"];
	converters     = ["strings"];
}
