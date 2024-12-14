import {Format} from "../../Format.js";

export class paintDotNetImage extends Format
{
	name       = "Paint.NET Image";
	website    = "http://fileformats.archiveteam.org/wiki/Paint.NET_image";
	ext        = [".pdn"];
	magic      = ["Paint.NET Image", /^Paint\.NET image data$/];
	converters = ["paintDotNet"];
}
