import {Format} from "../../Format.js";

export class package0000Archive extends Format
{
	name           = "0000 Package Archive";
	ext            = [".0000"];
	forbidExtMatch = true;
	magic          = [/^geArchive: 0000_package(_2)?( |$)/];	// eslint-disable-line unicorn/better-regex
	converters     = ["gameextractor[codes:0000_package_2,0000_package]"];
}
