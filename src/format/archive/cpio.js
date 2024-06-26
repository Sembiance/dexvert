import {Format} from "../../Format.js";

export class cpio extends Format
{
	name       = "CPIO";
	website    = "http://fileformats.archiveteam.org/wiki/Cpio";
	ext        = [".cpio"];
	magic      = ["CPIO archive", /cpio archive/, /^Cpio$/];
	converters = ["cpio", "sevenZip", "unar", "deark[module:cpio]"];
}
