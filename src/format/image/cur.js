import {Format} from "../../Format.js";

export class cur extends Format
{
	name         = "Microsoft Windows Cursor";
	website      = "http://fileformats.archiveteam.org/wiki/CUR";
	ext          = [".cur"];
	mimeType     = "application/ico";
	magic        = ["MS Windows cursor resource", "Microsoft Windows Cursor", "Windows Cursor shape", "deark: ico (Windows Cursor)", "deark: win1ico (Windows 1.0 cursor)", /^fmt\/385( |$)/];
	metaProvider = ["image"];
	converters   = ["deark[module:ico]", "iio2png", "deark[module:win1ico]", "gimp", "convert", "nconvert", "wuimg", "imconv[format:cur][matchType:magic]"];
}
