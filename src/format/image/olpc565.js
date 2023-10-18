import {Format} from "../../Format.js";

export class olpc565 extends Format
{
	name       = "One Laptop Per Child 565";
	website    = "http://fileformats.archiveteam.org/wiki/OLPC_565";
	ext        = [".565"];
	magic      = ["OLPC 565 bitmap", "OLPC firmware icon image data"];
	converters = ["deark[module:nsl]", "tomsViewer"];
}
