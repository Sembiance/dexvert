import {Format} from "../../Format.js";

export class photoLinePLD extends Format
{
	name           = "PhotoLine PLD";
	ext            = [".pld"];
	forbidExtMatch = true;
	magic          = ["PhotoLine :pld:"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="PhLD" && macFileCreator==="PhLn";
	converters     = ["nconvert[format:pld]"];
}
