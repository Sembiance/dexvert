import {Format} from "../../Format.js";

export class a2gsPreferred extends Format
{
	name       = "Apple IIGS Preferred Format";
	website    = "http://fileformats.archiveteam.org/wiki/Apple_II_graphics_formats";
	ext        = [".gs", ".iigs", ".pnt", ".shr"];
	magic      = ["Apple IIGS Preferred Format"];
	converters = ["recoil2png"];
	priority   = this.PRIORITY.LOW;
	verify     = ({meta}) => meta.colorCount>1;
}
