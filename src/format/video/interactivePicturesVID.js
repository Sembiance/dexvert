import {Format} from "../../Format.js";

export class interactivePicturesVID extends Format
{
	name           = "Interactive Pictures Video";
	ext            = [".evd", ".gvd", ".fvd"];
	forbidExtMatch = true;
	magic          = ["Interactive Pictures VID"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:ivd]"];
}
