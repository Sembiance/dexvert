import {Format} from "../../Format.js";

export class theDirector extends Format
{
	name        = "The Director Animation/Slideshow";
	website     = "https://www.computinghistory.org.uk/det/63951/The-Director/";
	ext         = [".film"];
	magic       = ["The Director animation/slideshow"];
	unsupported = true;	// 196 unique files on discmaster, but they don't appear to be very large and based on other files in the dir, seem to have a lot of external dependencies, so meh on support for now
}
