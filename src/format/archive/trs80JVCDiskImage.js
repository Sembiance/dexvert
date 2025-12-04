import {Format} from "../../Format.js";

export class trs80JVCDiskImage extends Format
{
	name           = "TRS/80 JVC Disk Image";
	ext            = [".jvc"];
	forbidExtMatch = true;
	fileSize       = 161_280;
	matchFileSize  = true;
	idCheck        = (inputFile, detections, {extMatch}) => !!extMatch;
	converters     = ["jvcextract"];
}
