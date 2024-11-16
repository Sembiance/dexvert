import {Format} from "../../Format.js";

export class woff extends Format
{
	name         = "Web Open Font Format";
	website      = "http://fileformats.archiveteam.org/wiki/WOFF";
	ext          = [".woff", ".woff2"];
	magic        = ["Web Open Font Format", "font/woff", "font/woff2", /^fmt\/(616|1172)( |$)/];
	metaProvider = ["fc_scan"];
	converters   = ["fontforge"];
	notes        = "Some fail to convert because their printable characters are icons and are in very high level charcodes and don't convert with imagemagick convert and thus fail verification.";
}
