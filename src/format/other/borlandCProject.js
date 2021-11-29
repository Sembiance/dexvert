import {Format} from "../../Format.js";

export class borlandCProject extends Format
{
	name           = "Borland C/C++ Project";
	ext            = [".prj"];
	forbidExtMatch = true;
	magic          = ["Borland Turbo C Project", "Borland C++"];
	converters     = ["strings"];
}
