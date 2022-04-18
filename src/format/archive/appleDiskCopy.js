import {Format} from "../../Format.js";

export class appleDiskCopy extends Format
{
	name       = "Apple DiskCopy";
	website    = "https://www.discferret.com/wiki/Apple_DiskCopy_4.2";
	magic      = ["Apple DiskCopy", "DiskCopy "];
	converters = ["dd[bs:84][skip:1] -> dexvert"];
}
