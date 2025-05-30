import {Format} from "../../Format.js";

export class cpio extends Format
{
	name       = "CPIO";
	website    = "http://fileformats.archiveteam.org/wiki/Cpio";
	ext        = [".cpio"];
	magic      = ["CPIO archive", "application/x-cpio", /cpio archive/, /^Cpio$/, "deark: cpio (cpio", /^fmt\/635( |$)/];
	converters = ["cpio", "sevenZip", "unar", "deark[module:cpio]"];
}
