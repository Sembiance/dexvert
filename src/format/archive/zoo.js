import {Format} from "../../Format.js";

export class zoo extends Format
{
	name       = "Zoo Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Zoo";
	ext        = [".zoo"];
	magic      = ["ZOO compressed archive", "Zoo archive data", /^Zoo$/, /^x-fmt\/269( |$)/];
	converters = ["zoo", "deark[module:zoo]", "unar", "izArc", "UniExtract"];
}
