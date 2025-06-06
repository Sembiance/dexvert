import {Format} from "../../Format.js";

export class ripIcon extends Format
{
	name       = "RIP Icon";
	website    = "http://fileformats.archiveteam.org/wiki/RIPscrip_Icon";
	ext        = [".icn"];
	magic      = ["deark: ripicon"];	// "RIPTerm Image :ript:" is too weak and steals hpPalmtopIcon
	priority   = this.PRIORITY.HIGH;	// such a generic extension, but set high priority due to giving deark an explict module to use which seems to fail properly
	converters = ["deark[module:ripicon]"];	// nconvert messes up most of the colors
}
