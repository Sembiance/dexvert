import {Format} from "../../Format.js";

export class tim extends Format
{
	name         = "PlayStation TIM";
	website      = "http://fileformats.archiveteam.org/wiki/TIM_(PlayStation_graphics)";
	ext          = [".tim"];
	magic        = ["TIM image", "PSX TIM", "deark: tim", "TIM PSX :tim:", "image:Sony.TimFormat", /^geViewer: TIM( |$)/];
	weakMagic    = ["TIM image", "PSX TIM"];
	metaProvider = ["image"];
	converters   = [
		"convert", "deark[module:tim]", "wuimg[format:tim]", "nconvert[format:tim]", "gameextractor[renameOut][codes:TIM]",
		"GARbro[types:image:Sony.TimFormat][matchType:magic]", "paintDotNet[matchType:magic]", "noesis[type:image]",
		"recoil2png[format:TIM]"
	];
}
