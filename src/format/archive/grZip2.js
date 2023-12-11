import {Format} from "../../Format.js";

export class grZip2 extends Format
{
	name       = "GrZip II Compressed File";
	magic      = ["GRZipII compressed archive"];
	packed     = true;
	converters = ["grZip2"];
}
