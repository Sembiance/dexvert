import {Format} from "../../Format.js";

export class canDoDeck extends Format
{
	name           = "CanDo Deck";
	website        = "https://cando.amigacity.xyz/index.php/downloads/category/7-cando-software";
	ext            = [".deck"];
	forbidExtMatch = true;
	magic          = ["CanDo Deck"];
	unsupported    = true;
	notes          = "Could use 'DeckViewer' from above, or something else to view/convert. More info: https://randocity.com/2018/03/27/cando-an-amiga-programming-language/";
}
