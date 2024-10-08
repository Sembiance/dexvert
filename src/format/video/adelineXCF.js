import {Format} from "../../Format.js";

export class adelineXCF extends Format
{
	name           = "Adeline XCF video";
	website        = "https://wiki.multimedia.cx/index.php/Adeline_XCF";
	ext            = [".acf"];
	forbidExtMatch = true;
	magic          = ["Adeline XCF Video"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:acf]"];
}
