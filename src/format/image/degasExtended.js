import {Format} from "../../Format.js";

export class degasExtended extends Format
{
	name       = "Extended DEGAS Image";
	website    = "http://fileformats.archiveteam.org/wiki/Extended_DEGAS_image";
	ext        = [".pi4", ".pi5", ".pi6", ".pi7", ".pi8", ".pi9"];
	fileSize   = {".pi4" : [77824, 154_114], ".pi5" : 153_634, ".pi7" : 308_224, ".pi9" : [77824, 65024]};
	byteCheck  = [{ext : ".pi5", offset : 0, match : [0x00, 0x04]}];
	converters = ["recoil2png"];
}
