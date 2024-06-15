import {Format} from "../../Format.js";

export class compressionWorkshopArchive extends Format
{
	name       = "Compression Workshop Archive";
	website    = "https://github.com/geneb/CompressionWorkshop";
	ext        = [".cwf"];
	magic      = ["Compression Workshop compressed archive"];
	converters = ["cwunpack"];
}
