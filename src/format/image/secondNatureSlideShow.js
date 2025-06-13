import {Format} from "../../Format.js";

export class secondNatureSlideShow extends Format
{
	name       = "Second Nature Slide Show";
	ext        = [".cat"];
	magic      = ["Second Nature Slide Show"];
	converters = ["deark[module:jpegscan]"];
}
