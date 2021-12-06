import {Format} from "../../Format.js";

export class samCoupeCOP extends Format
{
	name         = "Sam Coupe COP Module";
	ext          = [".cop"];
	notes        = "Not all files converted such as shanhai.cop";
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
