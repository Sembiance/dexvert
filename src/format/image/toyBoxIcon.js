import {Format} from "../../Format.js";

export class toyBoxIcon extends Format
{
	name           = "ToyBox Icon";
	website        = "http://fileformats.archiveteam.org/wiki/ToyBox_icon";
	ext            = [".tbi"];
	forbidExtMatch = true;
	magic          = ["deark: mdesk_icn (ToyBox icon)"];
	converters     = ["deark[module:mdesk_icn]"];
}
