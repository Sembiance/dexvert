import {Format} from "../../Format.js";

export class bbcMicro extends Format
{
	name       = "BBC Micro Image";
	website    = "http://fileformats.archiveteam.org/wiki/BBC_Micro_mode_image";
	ext        = [".bb0", ".bb1", ".bb2", ".bb4", ".bb5"];
	fileSize   = [10240, 20480];
	converters = ["recoil2png[format:BB4,BB0,BB5,BB1,BB2]"];
}
