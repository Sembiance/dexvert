import {Format} from "../../Format.js";

export class tim2TXC extends Format
{
	name           = "PlayStation 2 TIM2 TXC";
	website        = "http://fileformats.archiveteam.org/wiki/TIM2";
	ext            = [".txc"];
	forbidExtMatch = true;
	magic          = ["TIM PS2 :txc:"];
	converters     = ["nconvert[format:txc]"];
}
