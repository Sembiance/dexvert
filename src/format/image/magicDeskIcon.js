import {Format} from "../../Format.js";

export class magicDeskIcon extends Format
{
	name       = "MagicDesk Icon";
	website    = "http://fileformats.archiveteam.org/wiki/Magic_Desk_icon";
	ext        = [".icn"];
	fileSize   = 515;
	magic      = ["MagicDesk Icon"];
	converters = ["deark[module:mdesk_icn]"];
}
