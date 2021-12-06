import {Format} from "../../Format.js";

export class riffRaff extends Format
{
	name         = "Riff Raff Module";
	ext          = [".riff"];
	magic        = ["Riff Raff module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
