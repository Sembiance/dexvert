import {Format} from "../../Format.js";

export class xCarGraphics extends Format
{
	name       = "XCar Graphics/Bethesda GXA";
	ext        = [".gxa"];
	magic      = ["XCar Graphics"];
	converters = ["wuimg"];
}
