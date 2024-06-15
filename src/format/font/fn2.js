import {Format} from "../../Format.js";

export class fn2 extends Format
{
	name           = "Atari FontMaker";
	ext            = [".fn2", ".fnt", ".fn8"];
	forbidExtMatch = [".fnt"];
	safeExt        = ".fn2";
	fileSize       = 2048;
	converters     = ["recoil2png"];
}
