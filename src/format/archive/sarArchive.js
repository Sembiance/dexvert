import {Format} from "../../Format.js";

export class sarArchive extends Format
{
	name         = "SAR Archive";
	ext          = [".sar"];
	magic        = [/^SAR$/];
	keepFilename = true;
	converters   = ["unar"];
}
