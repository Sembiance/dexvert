import {Format} from "../../Format.js";

export class micrografxIcon extends Format
{
	name        = "Micrografx Icon";
	website     = "http://fileformats.archiveteam.org/wiki/Micrografx_Icon";
	ext         = [".icn"];
	magic       = ["Micrografx Icon", /^fmt\/1907( |$)/];
	unsupported = true;
	notes       = "No known converter.";
}
