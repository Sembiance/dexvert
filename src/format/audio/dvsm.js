import {Format} from "../../Format.js";

export class dvsm extends Format
{
	name           = "WinRec DVSM";
	website        = "https://temlib.org/AtariForumWiki/index.php/DVSM";
	ext            = [".dvs"];
	forbidExtMatch = true;
	magic          = ["DVSM Sample audio"];
	converters     = ["vibe2wav[renameOut]"];
}
