import {Format} from "../../Format.js";

export class deluxePaintAnimation extends Format
{
	name         = "DeluxePaint Animation";
	website      = "http://fileformats.archiveteam.org/wiki/DeluxePaint_Animation";
	ext          = [".anm"];
	magic        = ["DeluxePaint Animation", "Deluxe Paint Animation (anm)", /^fmt\/1363( |$)/];
	notes        = "Sample file HORSE.ANM doesn't convert for some reason";
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:anm]"];
}
