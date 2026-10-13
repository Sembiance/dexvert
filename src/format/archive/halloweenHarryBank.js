import {Format} from "../../Format.js";

export class halloweenHarryBank extends Format
{
	name           = "Halloween Harry Bank";
	ext            = [".bnk", ".fat"];
	forbidExtMatch = true;
	magic          = ["Halloween Harry Bank game data container"];
	auxFiles       = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.${input.ext.toLowerCase()===".bnk" ? "fat" : "bnk"}`);
	untouched      = ({f}) => f.input.ext.toLowerCase()===".fat";
	converters     = ["gameextractor[codes:0]", "gamearch[format:bnk-harry]"];
}
