import {Format} from "../../Format.js";

export class buildEngineRFFContainer extends Format
{
	name       = "Build Engine RFF Container";
	website    = "https://moddingwiki.shikadi.net/wiki/RFF_Format";
	ext        = [".rff"];
	magic      = ["Build Engine RFF encrypted container"];
	converters = ["gamearch"];
}
