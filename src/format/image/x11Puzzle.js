import {Format} from "../../Format.js";

export class x11Puzzle extends Format
{
	name       = "X11 Puzzle Image";
	website    = "http://fileformats.archiveteam.org/wiki/Puzzle_image_(X11)";
	ext        = [".cm", ".pzl"];
	magic      = ["deark: xpuzzle", "Puzzle :pzl:"];
	converters = ["deark[module:xpuzzle]", "nconvert[format:pzl]", "wuimg[matchType:magic]"];
	verify     = ({meta}) => meta.width>6 && meta.height>6;
}
