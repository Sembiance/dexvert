import {Format} from "../../Format.js";

export class realLivePDT extends Format
{
	name       = "RealLive PDT10 image";
	ext        = [".pdt"];
	magic      = ["RealLive PDT10 image"];
	converters = ["wuimg[matchType:magic]"];
}
