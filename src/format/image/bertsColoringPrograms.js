import {Format} from "../../Format.js";

export class bertsColoringPrograms extends Format
{
	name       = "Bert's Coloring Programs BMG";
	website    = "http://fileformats.archiveteam.org/wiki/BMG_(Bert%27s_Coloring_Programs)";
	ext        = [".bmg", ".ibg"];
	magic      = ["Zsoft Paintbrush :bmg:", "deark: berts_bmg"];
	converters = ["deark[module:berts_bmg][renameOut] -> convert"];	// nconvert[format:bmg] doesn't work right on things like ZEBRA.BMG
}
