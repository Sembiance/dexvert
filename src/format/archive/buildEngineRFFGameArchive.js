import {Format} from "../../Format.js";

export class buildEngineRFFGameArchive extends Format
{
	name           = "Build Engine RFF Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/RFF_Format";
	ext            = [".rff"];
	forbidExtMatch = true;
	magic          = ["Build Engine RFF encrypted container", /^geArchive: RFF_RFF( |$)/];
	converters     = ["gameextractor[codes:RFF_RFF]", "gamearch"];
}
