import {Format} from "../../Format.js";

export class seattleFilmWorks extends Format
{
	name         = "Seattle FilmWorks/PhotoWorks PhotoMail";
	website      = "http://fileformats.archiveteam.org/wiki/Seattle_FilmWorks";
	ext          = [".sfw", ".pwp", ".pwm", ".alb"];
	magic        = ["Seattle FilmWorks"];
	mimeType     = "image/x-seattle-filmworks";
	metaProvider = ["image"];
	converters   = ["convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
