import {Format} from "../../Format.js";

export class newIcon extends Format
{
	name       = "NewIcons Icon";
	website    = "http://fileformats.archiveteam.org/wiki/NewIcons";
	ext        = [".info"];
	magic      = ["Amiga NewIcon", "deark: amigaicon (Amiga Workbench Icon, NewIcons)"];
	converters = ["deark[module:amigaicon]"];
}
