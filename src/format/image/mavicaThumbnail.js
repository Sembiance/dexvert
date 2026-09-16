import {Format} from "../../Format.js";

export class mavicaThumbnail extends Format
{
	name           = "Mavica Thumbnail";
	ext            = [".411"];
	forbidExtMatch = true;
	magic          = ["Mavica Thumbnail :411:"];
	converters     = ["nconvert[format:411] "];
}
