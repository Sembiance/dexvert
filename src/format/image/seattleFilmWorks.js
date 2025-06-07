import {Format} from "../../Format.js";

export class seattleFilmWorks extends Format
{
	name         = "Seattle FilmWorks/PhotoWorks PhotoMail";
	website      = "http://fileformats.archiveteam.org/wiki/Seattle_FilmWorks";
	ext          = [".sfw", ".pwp", ".pwm", ".alb"];
	magic        = ["Seattle FilmWorks", "Seattle Film Works :sfw:", /^fmt\/1104( |$)/];
	mimeType     = "image/x-seattle-filmworks";
	metaProvider = ["image"];
	converters   = ["convert", `abydosconvert[format:${this.mimeType}]`, "nconvert[format:sfw]", "nconvert[format:pmp]"];	// the pmp is for a few that don't properly convert to sfw but are indeed SFW files
}
