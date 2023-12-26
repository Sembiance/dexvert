import {Format} from "../../Format.js";

export class windowsThumbDB extends Format
{
	name       = "Windows Thumbnail Database";
	website    = "http://fileformats.archiveteam.org/wiki/Thumbs.db";
	ext        = [".db"];
	filename   = ["Thumbs.db"];
	magic      = ["Windows Thumbnail Database", /^fmt\/682( |$)/];
	converters = ["vinetto", "deark[module:cfb]", "iio2png"];
}
