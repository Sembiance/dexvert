import {Format} from "../../Format.js";

export class gameCubeTHPAudio extends Format
{
	name             = "GameCube THP Audio";
	ext              = [".thp", ".dsp"];
	forbidExtMatch   = true;
	confidenceAdjust = () => -10;	// Reduce by 10 so that gameCubeTHPVideo matches first
	magic            = ["THP (thp)", "GameCube THP video", "vgmstream: thp", /^Nintendo THP Multimedia/];
	weakMagic        = true;
	converters       = ["ffmpeg[format:thp][libre][outType:mp3]", "vgmstream[types:thp]"];
}
