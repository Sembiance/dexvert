import {Format} from "../../Format.js";

export class squash extends Format
{
	name       = "SQUASH Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Squash_(RISC_OS)";
	magic      = ["squished archive data", "Squash compressed data", "Archive: Squash compressor", "deark: squash"];
	notes      = "Alternative de-archiver I didn't try: https://github.com/mjwoodcock/riscosarc/";
	converters = ["deark[module:squash]"];
}
