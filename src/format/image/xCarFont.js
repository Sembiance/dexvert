import {Format} from "../../Format.js";

export class xCarFont extends Format
{
	name           = "XCar Font";
	ext            = [".fnt"];
	forbidExtMatch = true;
	magic          = ["XCar Font"];
	converters     = ["wuimg -> *montage"];
}
