import {Format} from "../../Format.js";

export class frontRunnerBinaryModule extends Format
{
	name           = "FrontRunner Binary Module";
	ext            = [".frb"];
	forbidExtMatch = true;
	magic          = ["FrontRunner Binary module"];
	converters     = ["strings"];
}
