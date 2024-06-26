import {Format} from "../../Format.js";

export class ing extends Format
{
	name       = "ING 15";
	website    = "http://fileformats.archiveteam.org/wiki/ING_15";
	ext        = [".ing"];
	fileSize   = 16052;
	converters = ["recoil2png"];
	verify     = ({meta}) => meta.colorCount>1;
}
