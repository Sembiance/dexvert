import {Format} from "../../Format.js";

export class printPartnerGraphics extends Format
{
	name       = "PrintPartner Graphics Bitmaps";
	website    = "http://fileformats.archiveteam.org/wiki/PrintPartner";
	ext        = [".gph"];
	magic      = ["PrintPartner Graphic bitmaps"];
	converters = ["deark[module:pp_gph]"];
}
