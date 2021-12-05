import {Format} from "../../Format.js";

export class dvsm extends Format
{
	name        = "WinRec DVSM";
	website     = "https://temlib.org/AtariForumWiki/index.php/DVSM";
	ext         = [".dvs"];
	magic       = ["DVSM Sample audio"];
	unsupported = true;
	notes       = "No known linux/windows/amiga converter";
}
