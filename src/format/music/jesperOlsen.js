import {xu} from "xu";
import {Format} from "../../Format.js";

export class jesperOlsen extends Format
{
	name         = "Jesper Olsen Module";
	ext          = [".jo"];
	magic        = ["TTComp archive"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:JesperOlsen]", "uade123[player:JesperOlsen_EP]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
