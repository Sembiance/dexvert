import {Format} from "../../Format.js";

export class windowsThumbDB extends Format
{
	name       = "Windows Thumbnail Database";
	website    = "http://fileformats.archiveteam.org/wiki/Windows_thumbnail_cache";
	ext        = [".db"];
	filename   = [/^Thumbs\.db$/];
	magic      = [
		// generic
		"Windows Thumbnail Database", /^fmt\/682( |$)/,

		// app specific
		"Corel PrintHouse image", "Corel Print Office image",
		/^fmt\/(1419|1420|1421)( |$)/
	];
	converters = ["vinetto", "deark[module:cfb]", "iio2png"];
}
