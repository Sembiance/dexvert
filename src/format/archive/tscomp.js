import {Format} from "../../Format.js";

export class tscomp extends Format
{
	name       = "The Sterling COMPressor archive";
	website    = "http://fileformats.archiveteam.org/wiki/TSComp";
	magic      = ["TSComp compressed data", "TSComp archive data"];
	converters = ["tscomp"];
}
