import {Format} from "../../Format.js";

export class yamahaSMAF extends Format
{
	name        = "Yamaha Synthetic Music Mobile Application Format";
	website     = "https://lpcwiki.miraheze.org/wiki/Yamaha_SMAF";
	ext         = [".mmf"];
	magic       = ["Yamaha SMAF", "application/vnd.smaf", /^fmt\/1178( |$)/];
	unsupported = true;
}
