import {Format} from "../../Format.js";

export class magicDeskIcon extends Format
{
	name       = "MagicDesk Icon";
	website    = "http://fileformats.archiveteam.org/wiki/Magic_Desk_icon";
	ext        = [".icn"];
	idCheck    = inputFile => inputFile.size%515===0;
	magic      = ["MagicDesk Icon"];
	converters = ["deark[module:mdesk_icn]"];
}
