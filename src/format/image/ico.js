import {Format} from "../../Format.js";

export class ico extends Format
{
	name       = "Microsoft Windows Icon File";
	website    = "http://fileformats.archiveteam.org/wiki/ICO";
	ext        = [".ico"];
	magic      = [/^Windows Icon$/, /^Windows Icon \(even big\)$/, "MS Windows icon resource", "Icon File Format", /^x-fmt\/418( |$)/];
	idMeta     = ({macFileType}) => macFileType==="ICO ";
	trustMagic = true;

	// ICO file has multiple sub icons, which deark handles well and iio2png also supports. Fallback to nconvert. pv can also convert, but often produces garbage.
	converters = ["deark[module:ico]", "iio2png", "deark[module:win1ico]", "iconvert", "nconvert", "gimp", "imconv[format:ico]", "hiJaakExpress", "canvas5[strongMatch]"];
}
