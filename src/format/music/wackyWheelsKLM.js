import {Format} from "../../Format.js";

export class wackyWheelsKLM extends Format
{
	name       = "Wacky Wheels KLM";
	website    = "https://moddingwiki.shikadi.net/wiki/KLM_Format";
	ext        = [".klm"];
	converters = ["gamemus[format:klm-wacky]"];
}
