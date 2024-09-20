import {Format} from "../../Format.js";

export class sfd extends Format
{
	name       = "FontForge File Format";
	website    = "http://fileformats.archiveteam.org/wiki/Spline_Font_Database";
	ext        = [".sfd"];
	magic      = ["Spline Font Database", "application/vnd.font-fontforge-sfd"];
	converters = ["fontforge"];
}
