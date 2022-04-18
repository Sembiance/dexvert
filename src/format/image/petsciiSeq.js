import {Format} from "../../Format.js";

export class petsciiSeq extends Format
{
	name        = "PETSCII Screen Code Sequence";
	website     = "http://fileformats.archiveteam.org/wiki/PETSCII";
	ext         = [".seq"];
	mimeType    = "text/x-petscii-sequence";
	unsupported = true;
	notes       = "Can't reliably detect this format and abydosconvert will convert a lot of things that end in .seq thare are not PETSCII code sequences";
	converters  = [`abydosconvert[format:${this.mimeType}]`];
}

