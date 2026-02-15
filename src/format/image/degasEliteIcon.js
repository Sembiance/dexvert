import {Format} from "../../Format.js";

export class degasEliteIcon extends Format
{
	name       = "DEGAS Elite Icon";
	website    = "http://fileformats.archiveteam.org/wiki/DEGAS_Elite_icon";
	ext        = [".icn"];
	magic      = ["DEGAS Elite Icon Definition"];
	converters = ["recoil2png[format:ICN.StIcn]", "wuimg[format:c]"];
}
