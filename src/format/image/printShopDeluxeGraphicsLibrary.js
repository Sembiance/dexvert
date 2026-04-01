import {Format} from "../../Format.js";

export class printShopDeluxeGraphicsLibrary extends Format
{
	name        = "Print Shop Deluxe Graphics Library";
	ext         = [".psg"];
	magic       = ["The Print Shop Deluxe Graphics library"];
	unsupported = true;	// vibe coded an extractor, but due to being vector based images, couldn't reverse engineer the drawing commands. see sandbox/app/printShopDeluxeGraphicsLibrary/
	notes       = "No known extractor program.";
}
