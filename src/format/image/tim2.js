import {Format} from "../../Format.js";

export class tim2 extends Format
{
	name           = "PlayStation 2 TIM2";
	website        = "http://fileformats.archiveteam.org/wiki/TIM2";
	ext            = [".tm2", ".tim2", ".tim"];
	forbidExtMatch = true;
	magic          = ["TIM2 PlayStation2 bitmap", "TIM PS2 :tim2:"];
	converters     = ["nconvert[format:tim2]"];
}
