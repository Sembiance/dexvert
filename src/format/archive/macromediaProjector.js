import {Format} from "../../Format.js";

export class macromediaProjector extends Format
{
	name       = "Macromedia Projector";
	magic      = ["Macromedia Projector (Mac)", "Macromedia Projector (Win)", /MacBinary II.+creator 'PJ93'/];
	converters = ["director_files_extract"];
}
