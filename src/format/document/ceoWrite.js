import {Format} from "../../Format.js";

export class ceoWrite extends Format
{
	name        = "CEOWrite";
	website     = "https://en.wikipedia.org/wiki/Data_General";
	ext         = [".cw"];
	unsupported = true;
	converters  = ["softwareBridge[format:ceoWrite]"];
	notes       = "Old word processor. Haven't investigated it for magic.";
}
