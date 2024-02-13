import {Format} from "../../Format.js";

export class imageUSB extends Format
{
	name           = "imageUSB";
	website        = "https://forums.passmark.com/other-software/5213-opening-imageusb-bin-output-file-with-different-software";
	ext            = [".usbimage"];
	forbidExtMatch = true;
	magic          = ["imageUSB"];

	// Must be greater than 512 bytes in length, since that's how long the imageUSB header is
	idCheck = inputFile => inputFile.size>512;

	// Just output the original file without the 512 byte header
	converters = ["dd[bs:512][skip:1]"];
}
