import {Format} from "../../Format.js";

export class turboBASICChainModule extends Format
{
	name           = "Turbo Basic Chain module";
	ext            = [".tbc"];
	forbidExtMatch = true;
	magic          = ["Turbo Basic compiled Chain module"];
	converters     = ["strings"];
}
