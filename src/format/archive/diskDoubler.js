import {Format} from "../../Format.js";

export class diskDoubler extends Format
{
	name         = "Disk Doubler";
	ext          = [".dd"];
	keepFilename = true;
	magic        = ["Disk Doubler compressed data", /^DiskDoubler$/, /^fmt\/1399( |$)/];
	converters   = ["unar", "macunpack"];
}
