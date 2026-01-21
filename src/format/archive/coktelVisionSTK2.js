import {Format} from "../../Format.js";

export class coktelVisionSTK2 extends Format
{
	name           = "Coktel Vision STK2 Archive ";
	ext            = [".itk"];
	forbidExtMatch = true;
	magic          = ["Coktel Vision STK2 Archive"];
	converters     = ["na_game_tool_extract[format:stk2]"];
}
