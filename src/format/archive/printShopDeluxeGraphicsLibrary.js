import {Format} from "../../Format.js";

export class printShopDeluxeGraphicsLibrary extends Format
{
	name        = "Print Shop Deluxe Graphics Library";
	ext         = [".psg"];
	magic       = ["The Print Shop Deluxe Graphics library", /^x-fmt\/168( |$)/];
	unsupported = true;
	notes       = "No known extractor program.";
}
