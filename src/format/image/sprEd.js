import {Format} from "../../Format.js";

export class sprEd extends Format
{
	name           = "SprEd Sprite";
	ext            = [".spr"];
	forbidExtMatch = true;
	magic          = ["SprEd Sprite"];
	converters     = ["recoil2png[format:SPR.SprEd,SPR.Atari8Spr]"];
}
