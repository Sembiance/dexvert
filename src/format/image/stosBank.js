import {Format} from "../../Format.js";

export class stosBank extends Format
{
	name       = "STOS Memory Bank";
	website    = "http://fileformats.archiveteam.org/wiki/STOS_memory_bank";
	ext        = [".mbk", ".mbs"];
	mimeType   = "application/x-stos-memorybank";
	magic      = ["STOS Memory Bank", "STOS data", /^fmt\/1467( |$)/];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
