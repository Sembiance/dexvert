import {Format} from "../../Format.js";

export class seuckSprite extends Format
{
	name          = "Shoot 'Em Up Construction Kit Sprite";
	website       = "http://fileformats.archiveteam.org/wiki/Shoot_'Em_Up_Construction_Kit";
	ext           = [".a"];
	safeExt       = ".a";
	fileSize      = 8130;
	matchFileSize = true;
	converters    = ["recoil2png"];
}
