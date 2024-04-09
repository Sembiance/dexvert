import {xu} from "xu";
import {Format} from "../../Format.js";

export class titanics extends Format
{
	name         = "Titanics Module";
	ext          = [".tip"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
