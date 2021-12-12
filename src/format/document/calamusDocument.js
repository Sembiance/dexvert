import {Format} from "../../Format.js";

export class calamusDocument extends Format
{
	name        = "Calamus Document";
	website     = "http://fileformats.archiveteam.org/wiki/Calamus";
	ext         = [".cdk"];
	magic       = ["Calamus Document"];
	unsupported = true;
}
