import {Format} from "../../Format.js";

export class kfx extends Format
{
	name       = "Atari KFX";
	website    = "http://fileformats.archiveteam.org/wiki/KFX_(Atari_graphics_format)";
	ext        = [".kfx"];
	converters = ["recoil2png[format:KFX]"];
}
