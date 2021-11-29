import {Format} from "../../Format.js";

export class turboDebuggerConfig extends Format
{
	name           = "Turbo Debugger Configuration";
	ext            = [".td", ".td2"];
	forbidExtMatch = true;
	magic          = ["Turbo Debugger configuration"];
	converters     = ["strings"];
}
