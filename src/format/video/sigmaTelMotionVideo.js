import {Format} from "../../Format.js";

export class sigmaTelMotionVideo extends Format
{
	name           = "Sigma Tel Motion Video";
	website        = "https://wiki.multimedia.cx/index.php/SMV";
	ext            = [".smv"];
	forbidExtMatch = true;
	magic          = ["SigmaTel Motion Video"];
	converters     = ["ffmpeg"];
}
