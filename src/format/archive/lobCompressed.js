import {Format} from "../../Format.js";

export class lobCompressed extends Format
{
	name       = "LOB Compressed";
	magic      = ["LOB compressed Amiga executable", "LOB: LOB's File Compressor", "Archive: LOB's File Compressor"];
	packed     = true;
	converters = ["ancient"];
}
