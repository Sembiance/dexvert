import {Format} from "../../Format.js";

export class multiTracker extends Format
{
	name         = "MultiTracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Multi_Track_Module";
	ext          = [".mtm"];
	magic        = [/^Multi[Tt]racker /];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
