import {Format} from "../../Format.js";

export class petsciiSeq extends Format
{
	name        = "PETSCII Screen Code Sequence";
	website     = "http://fileformats.archiveteam.org/wiki/PETSCII";
	ext         = [".seq"];
	mimeType    = "text/x-petscii-sequence";
	unsupported = true;	// can't reliably detect as extension isn't even reliable and abydosconvert will convert anything
	converters  = [`abydosconvert[format:${this.mimeType}]`];
}

