import {Format} from "../../Format.js";

export class selectWareArchive extends Format
{
	name           = "SelectWare Technologies archive";
	website        = "https://moddingwiki.shikadi.net/wiki/SelectWare_Archive";
	ext            = [".swt"];
	forbidExtMatch = true;
	magic          = ["SelectWare Technologies archive"];
	converters     = ["unSelectWare"];
}
