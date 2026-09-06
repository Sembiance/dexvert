import {Format} from "../../Format.js";

export class digDemoFL2 extends Format
{
	name           = "D.i.G demo FL2";
	ext            = [".fl2"];
	forbidExtMatch = true;
	magic          = ["D.i.G demo FL2"];
	converters     = ["na_game_tool_extract[format:fl2]"];
}

