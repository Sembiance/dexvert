import {Format} from "../../Format.js";

export class bld extends Format
{
	name       = "MegaPaint BLD";
	website    = "http://fileformats.archiveteam.org/wiki/MegaPaint_BLD";
	ext        = [".bld"];
	converters = ["deark[module:bld]", "recoil2png"];

	// If it fails, it often produces a 1x65535 image, so exclude those
	verify = ({meta}) => meta.width>1 && meta.height>1 && meta.width<4000 && meta.height<4000;
}
