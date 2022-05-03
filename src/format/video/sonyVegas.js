import {Format} from "../../Format.js";

export class sonyVegas extends Format
{
	name        = "Sony Vegas Video";
	website     = "https://en.wikipedia.org/wiki/Vegas_Pro";
	ext         = [".veg"];
	magic       = ["Sony Vegas video project"];
	unsupported = true;
}
