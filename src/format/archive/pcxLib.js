import {Format} from "../../Format.js";

export class pcxLib extends Format
{
	name       = "PCXlib Compressed Archive";
	website    = "http://fileformats.archiveteam.org/wiki/PCX_Library";
	ext        = [".pcl"];
	magic      = ["pcxLib compressed", "PCX Library game data container"];
	converters = ["deark[module:pcxlib]", "unpcxgx"];
}
