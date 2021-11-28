import {Format} from "../../Format.js";

export class sge extends Format
{
	name       = "Semi-Graphics Logos Editor";
	website    = "http://fileformats.archiveteam.org/wiki/Semi-Graphic_logos_Editor";
	ext        = [".sge"];
	converters = ["recoil2png"];
}
