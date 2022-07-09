import {Format} from "../../Format.js";

export class delphineCIN extends Format
{
	name        = "Delphine CIN Video";
	website     = "https://wiki.multimedia.cx/index.php/Delphine_CIN";
	ext         = [".cin"];
	magic       = ["Delphine CIN video"];
	unsupported = true;
	notes       = "FFMPEG has support for something called Delphine Software International CIN, but it couldn't convert the test files";
}
