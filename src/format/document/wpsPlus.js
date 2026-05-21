import {Format} from "../../Format.js";

export class wpsPlus extends Format
{
	name        = "DEC WPS-PLUS DX";
	website     = "https://winworldpc.com/product/wps-plus/1x";
	ext         = [".dx"];
	unsupported = true;	// no known magic, unlikely to have many on discmaster anyways due to being VAX based
	converters  = ["softwareBridge[format:wpsPlusDX]"];
}
