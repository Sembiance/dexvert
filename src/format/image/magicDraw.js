import {Format} from "../../Format.js";

export class magicDraw extends Format
{
	name       = "Magic Draw";
	website    = "http://fileformats.archiveteam.org/wiki/MagicDraw";
	ext        = [".shr", ".hr"];
	converters = ["recoil2png"];
	verify     = ({meta}) => meta.colorCount>1;
}
