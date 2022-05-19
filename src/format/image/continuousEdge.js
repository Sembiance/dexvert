import {Format} from "../../Format.js";

export class continuousEdge extends Format
{
	name        = "Continuous Edge Graphic Bitmap";
	ext         = [".ceg"];
	magic       = ["Continuous Edge Graphic bitmap"];
	unsupported = true;
	notes       = "PV says it can convert these, but didn't work on my 1 and only sample file.";
}
