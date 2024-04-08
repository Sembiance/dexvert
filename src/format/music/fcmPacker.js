import {Format} from "../../Format.js";

export class fcmPacker extends Format
{
	name         = "FC-M Packer Song";
	website      = "http://fileformats.archiveteam.org/wiki/FC-M_Packer_module";
	ext          = [".fcm"];
	magic        = ["FC-M Packer song/module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
}
