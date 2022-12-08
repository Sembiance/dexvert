import {Format} from "../../Format.js";

export class nokiaOperatorLogo extends Format
{
	name       = "Nokia Operator Logo";
	website    = "http://fileformats.archiveteam.org/wiki/Nokia_Operator_Logo";
	ext        = [".nol"];
	magic      = ["Nokia Operator Logo bitmap"];
	converters = ["deark", "nconvert"];
	verify     = ({meta}) => meta.width<5000 && meta.height<5000;
}
