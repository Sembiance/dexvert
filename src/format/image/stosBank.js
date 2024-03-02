import {Format} from "../../Format.js";

export class stosBank extends Format
{
	name       = "STOS Memory Bank";
	website    = "http://fileformats.archiveteam.org/wiki/STOS_memory_bank";
	ext        = [".mbk", ".mbs"];
	mimeType   = "application/x-stos-memorybank";
	magic      = ["STOS Memory Bank", "STOS data", /^fmt\/1467( |$)/];
	converters = [`deark[module:stos]`, `abydosconvert[format:${this.mimeType}]`];	// if multiple images (SPRITES.MBK, MENUFONT.MBK) deark will extract multiple images which is preferred, abydosconvert will combine them into an animated webp
}
