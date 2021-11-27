import {Format} from "../../Format.js";

export class glowIcon extends Format
{
	name       = "Glow Icon";
	website    = "http://fileformats.archiveteam.org/wiki/GlowIcons";
	ext        = [".info"];
	magic      = ["Amiga GlowIcon"];
	converters = ["deark"]
}
