import {Format} from "../../Format.js";

export class hpPalmtopIcon extends Format
{
	name       = "HP Palmtop Icon";
	website    = "http://fileformats.archiveteam.org/wiki/HP_100LX/200LX_icon";
	ext        = [".icn", ".xbg"];
	magic      = [/HP Palmtop .*Icon$/];
	converters = ["deark"]
}
