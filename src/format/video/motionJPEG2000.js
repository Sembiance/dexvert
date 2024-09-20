import {Format} from "../../Format.js";

export class motionJPEG2000 extends Format
{
	name         = "Motion JPEG 2000";
	website      = "http://fileformats.archiveteam.org/wiki/MJ2";
	ext          = [".mj2", ".mjp2"];
	magic        = ["Motion JPEG 2000 video", "JPEG 2000 Part 3 (MJ2)", "video/mj2", /^fmt\/337( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
