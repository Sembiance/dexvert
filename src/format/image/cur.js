import {Format} from "../../Format.js";

export class cur extends Format
{
	name         = "Microsoft Windows Cursor";
	website      = "http://fileformats.archiveteam.org/wiki/CUR";
	ext          = [".cur"];
	mimeType     = "application/ico";
	magic        = ["MS Windows cursor resource", "Microsoft Windows Cursor", "Windows Cursor shape", /^fmt\/385( |$)/];
	metaProvider = ["image"];
	converters   = ["deark[module:ico]", "iio2png", "deark[module:win1ico]", "gimp", "convert", "nconvert", "imconv[format:cur]"];
}
