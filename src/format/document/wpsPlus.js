import {Format} from "../../Format.js";

export class wpsPlus extends Format
{
	name        = "DEC WPS-PLUS DX";
	website     = "https://winworldpc.com/product/wps-plus/1x";
	ext         = [".dx"];
	unsupported = true;
	converters  = ["softwareBridge[format:wpsPlusDX]"];
	notes       = "VAX based word processor. Haven't investigated it for magic.";
}
