import {Format} from "../../Format.js";

export class paintDotNetImage extends Format
{
	name       = "Paint.NET Image";
	ext        = [".pdn"];
	magic      = ["Paint.NET Image", /^Paint\.NET image data$/];
	converters = ["paintDotNet"];
}
