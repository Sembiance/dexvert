import {Format} from "../../Format.js";

export class wintermuteDCP extends Format
{
	name           = "Wintermust DCP Archive";
	website        = "https://gist.github.com/RomanKharin/10668624";
	ext            = [".dcp"];
	forbidExtMatch = true;
	magic          = ["Archive: DCP", "Wintermute DCP Archive"];
	converters     = ["quickbms[bms:wintermute_dcp]"];
}
