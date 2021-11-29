import {Format} from "../../Format.js";

export class turboPascalChainModule extends Format
{
	name           = "Turbo Pascal Chain module";
	ext            = [".chn"];
	forbidExtMatch = true;
	magic          = [/^Turbo Pascal [23].0 Chain module$/];
	converters     = ["strings"];
}
