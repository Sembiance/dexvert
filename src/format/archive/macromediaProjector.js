import {Format} from "../../Format.js";

export class macromediaProjector extends Format
{
	name       = "Macromedia Projector";
	magic      = ["Macromedia Projector (Mac)", "Macromedia Projector (Win)"];
	converters = ["director_files_extract"];
}
