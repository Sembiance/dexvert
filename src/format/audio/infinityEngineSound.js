import {Format} from "../../Format.js";

export class infinityEngineSound extends Format
{
	name           = "Infinity Engine Sound";
	ext            = [".wav"];
	forbidExtMatch = true;
	magic          = ["Infinity Engine sound"];
	converters     = ["vibe2wav[renameOut]"];
}
