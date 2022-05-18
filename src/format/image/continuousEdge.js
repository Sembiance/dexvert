import {Format} from "../../Format.js";

export class continuousEdge extends Format
{
	name        = "Continuous Edge Graphic Bitmap";
	ext         = [".ceg"];
	magic       = ["Continuous Edge Graphic bitmap"];
	unsupported = true;
	notes       = "No known converter.";
}
