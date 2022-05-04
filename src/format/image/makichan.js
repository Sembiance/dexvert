import {Format} from "../../Format.js";

export class makichan extends Format
{
	name       = "MAKIchan Graphic";
	website    = "http://fileformats.archiveteam.org/wiki/MAKIchan_Graphics";
	ext        = [".mag", ".max", ".mki"];
	magic      = [/^MAKI v1-[ab] bitmap$/, "MAG v2 bitmap", /^fmt\/1469( |$)/];
	converters = ["recoil2png"];
}
