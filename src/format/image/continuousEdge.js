import {Format} from "../../Format.js";

export class continuousEdge extends Format
{
	name           = "Continuous Edge Graphic Bitmap";
	ext            = [".ceg"];
	forbidExtMatch = true;
	magic          = ["Continuous Edge Graphic bitmap"];
	converters     = ["vibe2png"];
}
