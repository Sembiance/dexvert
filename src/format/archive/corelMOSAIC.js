import {Format} from "../../Format.js";

export class corelMOSAIC extends Format
{
	name       = "Corel MOSAIC Library Thumbnail Archive";
	website    = "http://fileformats.archiveteam.org/wiki/CorelMOSAIC_library";
	ext        = [".clb"];
	magic      = ["deark: corel_clb"];
	converters = ["deark[module:corel_clb]"];
}
