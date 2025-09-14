import {Format} from "../../Format.js";

export class windowsThumbDB extends Format
{
	name       = "Windows Thumbnail Database";
	website    = "http://fileformats.archiveteam.org/wiki/Windows_thumbnail_cache";
	ext        = [".db"];
	filename   = [/^Thumbs\.db$/];
	magic      = [
		// generic
		"Windows Thumbnail Database", "Windows thumbnail Data Base", "Windows thumbnails/icons cache", "deark: cfb (Thumbs.db)", /^fmt\/682( |$)/,

		// app specific
		"Corel PrintHouse image", "Corel Print Office image",
		/^fmt\/(1417|1418|1419|1420|1421)( |$)/
	];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="PHd1" && macFileCreator==="Cph1";
	converters = ["vinetto", "deark[module:cfb]", "iio2png"];
}
